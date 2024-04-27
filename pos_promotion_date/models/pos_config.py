from odoo import _, fields, models
from odoo.exceptions import UserError

class PosConfig(models.Model):
    _inherit = 'pos.config'

    def use_coupon_code(self, code, creation_date, partner_id):
        print('use_coupon_code')
        self.ensure_one()
        # Ordering by partner id to use the first assigned to the partner in case multiple coupons have the same code
        #  it could happen with loyalty programs using a code
        # Points desc so that in coupon mode one could use a coupon multiple times
        coupon = self.env['loyalty.card'].search(
            [('program_id', 'in', self._get_program_ids().ids), ('partner_id', 'in', (False, partner_id)), ('code', '=', code)],
            order='partner_id, points desc', limit=1)
        if not coupon or not coupon.program_id.active:
            return {
                'successful': False,
                'payload': {
                    'error_message': _('This coupon is invalid (%s).', code),
                },
            }
        check_date = fields.Date.from_string(creation_date[:11])
        print('check date',check_date)
        print('Today Date',fields.Date.context_today(self))
        print('program date',coupon.program_id.date_to)
        if (coupon.expiration_date and coupon.expiration_date < check_date) or\
            (coupon.program_id.date_to and coupon.program_id.date_to < fields.Date.context_today(self)) or\
            (coupon.program_id.limit_usage and coupon.program_id.total_order_count >= coupon.program_id.max_usage):
            return {
                'successful': False,
                'payload': {
                    'error_message': _('This coupon is expired (%s).', code),
                },
            }
        if not coupon.program_id.reward_ids or not any(reward.required_points <= coupon.points for reward in coupon.program_id.reward_ids):
            return {
                'successful': False,
                'payload': {
                    'error_message': _('No reward can be claimed with this coupon.'),
                },
            }
        return {
            'successful': True,
            'payload': {
                'program_id': coupon.program_id.id,
                'coupon_id': coupon.id,
                'coupon_partner_id': coupon.partner_id.id,
                'points': coupon.points,
                'has_source_order': coupon._has_source_order(),
            },
        }
