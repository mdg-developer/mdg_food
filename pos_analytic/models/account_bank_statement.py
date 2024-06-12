from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"
    
    def button_post(self):
        ''' Move the bank statements from 'draft' to 'posted'. '''
        if any(statement.state != 'open' for statement in self):
            raise UserError(_("Only new statements can be posted."))

        self._check_balance_end_real_same_as_computed()

        for statement in self:
            if not statement.name:
                statement._set_next_sequence()

        self.write({'state': 'posted'})
        if self.pos_session_id and self.journal_id.analytic_account_id:
            self.env.cr.execute("""update account_move_line
                                set analytic_account_id=%s
                                from account_bank_statement_line abs_line
                                where abs_line.move_id=account_move_line.move_id
                                and account_move_line.analytic_account_id is null;""", (self.journal_id.analytic_account_id.id,))
        lines_of_moves_to_post = self.line_ids.filtered(lambda line: line.move_id.state != 'posted')
        if lines_of_moves_to_post:
            lines_of_moves_to_post.move_id._post(soft=False)
    
class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"
    
    @api.model
    def _prepare_liquidity_move_line_vals(self):
        ''' Prepare values to create a new account.move.line record corresponding to the
        liquidity line (having the bank/cash account).
        :return:        The values to create a new account.move.line record.
        '''
        self.ensure_one()
        analytic_account_id = None
        
        statement = self.statement_id
        journal = statement.journal_id
        company_currency = journal.company_id.currency_id
        journal_currency = journal.currency_id if journal.currency_id != company_currency else False

        if self.foreign_currency_id and journal_currency:
            currency_id = journal_currency.id
            if self.foreign_currency_id == company_currency:
                amount_currency = self.amount
                balance = self.amount_currency
            else:
                amount_currency = self.amount
                balance = journal_currency._convert(amount_currency, company_currency, journal.company_id, self.date)
        elif self.foreign_currency_id and not journal_currency:
            amount_currency = self.amount_currency
            balance = self.amount
            currency_id = self.foreign_currency_id.id
        elif not self.foreign_currency_id and journal_currency:
            currency_id = journal_currency.id
            amount_currency = self.amount
            balance = journal_currency._convert(amount_currency, journal.company_id.currency_id, journal.company_id, self.date)
        else:
            currency_id = company_currency.id
            amount_currency = self.amount
            balance = self.amount

        vals = {
            'name': self.payment_ref,
            'move_id': self.move_id.id,
            'partner_id': self.partner_id.id,
            'currency_id': currency_id,
            'account_id': journal.default_account_id.id,
            'debit': balance > 0 and balance or 0.0,
            'credit': balance < 0 and -balance or 0.0,
            'amount_currency': amount_currency,
        }
        
        if self.statement_id.pos_session_id:       
            analytic_account_id = self.statement_id.journal_id.analytic_account_id.id
            vals['analytic_account_id'] = analytic_account_id
        return vals
    
    @api.model
    def _prepare_counterpart_move_line_vals(self, counterpart_vals, move_line=None):
        ''' Prepare values to create a new account.move.line move_line.
        By default, without specified 'counterpart_vals' or 'move_line', the counterpart line is
        created using the suspense account. Otherwise, this method is also called during the
        reconciliation to prepare the statement line's journal entry. In that case,
        'counterpart_vals' will be used to create a custom account.move.line (from the reconciliation widget)
        and 'move_line' will be used to create the counterpart of an existing account.move.line to which
        the newly created journal item will be reconciled.
        :param counterpart_vals:    A python dictionary containing:
            'balance':                  Optional amount to consider during the reconciliation. If a foreign currency is set on the
                                        counterpart line in the same foreign currency as the statement line, then this amount is
                                        considered as the amount in foreign currency. If not specified, the full balance is took.
                                        This value must be provided if move_line is not.
            'amount_residual':          The residual amount to reconcile expressed in the company's currency.
                                        /!\ This value should be equivalent to move_line.amount_residual except we want
                                        to avoid browsing the record when the only thing we need in an overview of the
                                        reconciliation, for example in the reconciliation widget.
            'amount_residual_currency': The residual amount to reconcile expressed in the foreign's currency.
                                        Using this key doesn't make sense without passing 'currency_id' in vals.
                                        /!\ This value should be equivalent to move_line.amount_residual_currency except
                                        we want to avoid browsing the record when the only thing we need in an overview
                                        of the reconciliation, for example in the reconciliation widget.
            **kwargs:                   Additional values that need to land on the account.move.line to create.
        :param move_line:           An optional account.move.line move_line representing the counterpart line to reconcile.
        :return:                    The values to create a new account.move.line move_line.
        '''
        self.ensure_one()

        statement = self.statement_id
        journal = statement.journal_id
        company_currency = journal.company_id.currency_id
        journal_currency = journal.currency_id or company_currency
        foreign_currency = self.foreign_currency_id or journal_currency or company_currency
        statement_line_rate = (self.amount_currency / self.amount) if self.amount else 0.0

        balance_to_reconcile = counterpart_vals.pop('balance', None)
        amount_residual = -counterpart_vals.pop('amount_residual', move_line.amount_residual if move_line else 0.0) \
            if balance_to_reconcile is None else balance_to_reconcile
        amount_residual_currency = -counterpart_vals.pop('amount_residual_currency', move_line.amount_residual_currency if move_line else 0.0)\
            if balance_to_reconcile is None else balance_to_reconcile

        if 'currency_id' in counterpart_vals:
            currency_id = counterpart_vals['currency_id'] or company_currency.id
        elif move_line:
            currency_id = move_line.currency_id.id or company_currency.id
        else:
            currency_id = foreign_currency.id

        if currency_id not in (foreign_currency.id, journal_currency.id):
            currency_id = company_currency.id
            amount_residual_currency = 0.0

        amounts = {
            company_currency.id: 0.0,
            journal_currency.id: 0.0,
            foreign_currency.id: 0.0,
        }

        amounts[currency_id] = amount_residual_currency
        amounts[company_currency.id] = amount_residual

        if currency_id == journal_currency.id and journal_currency != company_currency:
            if foreign_currency != company_currency:
                amounts[company_currency.id] = journal_currency._convert(amounts[currency_id], company_currency, journal.company_id, self.date)
            if statement_line_rate:
                amounts[foreign_currency.id] = amounts[currency_id] * statement_line_rate
        elif currency_id == foreign_currency.id and self.foreign_currency_id:
            if statement_line_rate:
                amounts[journal_currency.id] = amounts[foreign_currency.id] / statement_line_rate
                if foreign_currency != company_currency:
                    amounts[company_currency.id] = journal_currency._convert(amounts[journal_currency.id], company_currency, journal.company_id, self.date)
        else:
            amounts[journal_currency.id] = company_currency._convert(amounts[company_currency.id], journal_currency, journal.company_id, self.date)
            if statement_line_rate:
                amounts[foreign_currency.id] = amounts[journal_currency.id] * statement_line_rate

        if foreign_currency == company_currency and journal_currency != company_currency and self.foreign_currency_id:
            balance = amounts[foreign_currency.id]
        else:
            balance = amounts[company_currency.id]

        if foreign_currency != company_currency and self.foreign_currency_id:
            amount_currency = amounts[foreign_currency.id]
            currency_id = foreign_currency.id
        elif journal_currency != company_currency and not self.foreign_currency_id:
            amount_currency = amounts[journal_currency.id]
            currency_id = journal_currency.id
        else:
            amount_currency = amounts[company_currency.id]
            currency_id = company_currency.id

        vals = {
            **counterpart_vals,
            'name': counterpart_vals.get('name', move_line.name if move_line else ''),
            'move_id': self.move_id.id,
            'partner_id': self.partner_id.id or (move_line.partner_id.id if move_line else False),
            'currency_id': currency_id,
            'account_id': counterpart_vals.get('account_id', move_line.account_id.id if move_line else False),
            'debit': balance if balance > 0.0 else 0.0,
            'credit': -balance if balance < 0.0 else 0.0,
            'amount_currency': amount_currency,
        }
        
        if self.statement_id.pos_session_id:
            analytic_account_id = self.statement_id.journal_id.analytic_account_id.id
            vals['analytic_account_id'] = analytic_account_id
        return vals


class AccountPayment(models.Model):
    _inherit = "account.payment"


    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        ''' Prepare the dictionary to create the default account.move.lines for the current payment.
        :param write_off_line_vals: Optional dictionary to create a write-off account.move.line easily containing:
            * amount:       The amount to be added to the counterpart amount.
            * name:         The label to set on the line.
            * account_id:   The account on which create the write-off.
        :return: A list of python dictionary to be passed to the account.move.line's 'create' method.
        '''
        self.ensure_one()
        write_off_line_vals = write_off_line_vals or {}

        if not self.outstanding_account_id:
            raise UserError(_(
                "You can't create a new payment without an outstanding payments/receipts account set either on the company or the %s payment method in the %s journal.",
                self.payment_method_line_id.name, self.journal_id.display_name))

        # Compute amounts.
        write_off_amount_currency = write_off_line_vals.get('amount', 0.0)

        if self.payment_type == 'inbound':
            # Receive money.
            liquidity_amount_currency = self.amount
        elif self.payment_type == 'outbound':
            # Send money.
            liquidity_amount_currency = -self.amount
            write_off_amount_currency *= -1
        else:
            liquidity_amount_currency = write_off_amount_currency = 0.0

        write_off_balance = self.currency_id._convert(
            write_off_amount_currency,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        liquidity_balance = self.currency_id._convert(
            liquidity_amount_currency,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        counterpart_amount_currency = -liquidity_amount_currency - write_off_amount_currency
        counterpart_balance = -liquidity_balance - write_off_balance
        currency_id = self.currency_id.id

        if self.is_internal_transfer:
            if self.payment_type == 'inbound':
                liquidity_line_name = _('Transfer to %s', self.journal_id.name)
            else:  # payment.payment_type == 'outbound':
                liquidity_line_name = _('Transfer from %s', self.journal_id.name)
        else:
            liquidity_line_name = self.payment_reference

        # Compute a default label to set on the journal items.

        payment_display_name = self._prepare_payment_display_name()

        default_line_name = self.env['account.move.line']._get_default_line_name(
            _("Internal Transfer") if self.is_internal_transfer else payment_display_name[
                '%s-%s' % (self.payment_type, self.partner_type)],
            self.amount,
            self.currency_id,
            self.date,
            partner=self.partner_id,
        )
        analytic_account_id = False
        if self.journal_id.analytic_account_id:
            analytic_account_id = self.journal_id.analytic_account_id.id

        line_vals_list = [
            # Liquidity line.
            {
                'name': liquidity_line_name or default_line_name,
                'date_maturity': self.date,
                'amount_currency': liquidity_amount_currency,
                'currency_id': currency_id,
                'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
                'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.outstanding_account_id.id,
                'analytic_account_id': analytic_account_id,
            },
            # Receivable / Payable.
            {
                'name': self.payment_reference or default_line_name,
                'date_maturity': self.date,
                'amount_currency': counterpart_amount_currency,
                'currency_id': currency_id,
                'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
                'credit': -counterpart_balance if counterpart_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.destination_account_id.id,
                'analytic_account_id': analytic_account_id,

            },
        ]
        if not self.currency_id.is_zero(write_off_amount_currency):
            # Write-off line.
            line_vals_list.append({
                'name': write_off_line_vals.get('name') or default_line_name,
                'amount_currency': write_off_amount_currency,
                'currency_id': currency_id,
                'debit': write_off_balance if write_off_balance > 0.0 else 0.0,
                'credit': -write_off_balance if write_off_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': write_off_line_vals.get('account_id'),
                'analytic_account_id': analytic_account_id,

            })
        return line_vals_list