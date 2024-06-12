from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _validate_session(self, balancing_account=False, amount_to_balance=0, bank_payment_method_diffs=None):
        # import pdb
        # pdb.set_trace()
        bank_payment_method_diffs = bank_payment_method_diffs or {}
        self.ensure_one()
        sudo = self.user_has_groups('point_of_sale.group_pos_user')
        if self.order_ids or self.statement_ids.line_ids:
            self.cash_real_transaction = self.cash_register_total_entry_encoding
            self.cash_real_expected = self.cash_register_balance_end
            self.cash_real_difference = self.cash_register_difference
            if self.state == 'closed':
                raise UserError(_('This session is already closed.'))
            self._check_if_no_draft_orders()
            self._check_invoices_are_posted()
            if self.update_stock_at_closing:
                self._create_picking_at_end_of_session()
                self.order_ids.filtered(lambda o: not o.is_total_cost_computed)._compute_total_cost_at_session_closing(self.picking_ids.move_lines)
            try:
                data = self.with_company(self.company_id)._create_account_move(balancing_account, amount_to_balance, bank_payment_method_diffs)
            except AccessError as e:
                if sudo:
                    data = self.sudo().with_company(self.company_id)._create_account_move(balancing_account, amount_to_balance, bank_payment_method_diffs)
                else:
                    raise e

            try:
                balance = sum(self.move_id.line_ids.mapped('balance'))
                self.move_id._check_balanced()
            except UserError:
               
                self.env.cr.rollback()
                return self._close_session_action(balance)

            if self.move_id.line_ids:
                if self.move_id.journal_id.analytic_account_id:
                    self.env.cr.execute('update account_move_line set analytic_account_id=%s where move_id=%s', (self.move_id.journal_id.analytic_account_id.id,self.move_id.id,))
                self.move_id.sudo().with_company(self.company_id)._post()
                # Set the uninvoiced orders' state to 'done'
                self.env['pos.order'].search([('session_id', '=', self.id), ('state', '=', 'paid')]).write({'state': 'done'})
            else:
                self.move_id.sudo().unlink()
            self.sudo().with_company(self.company_id)._reconcile_account_move_lines(data)
        else:
            statement = self.cash_register_id
            if not self.config_id.cash_control:
                statement.write({'balance_end_real': statement.balance_end})
            statement.button_post()
            statement.button_validate()
        self.write({'state': 'closed'})
        return True
        