from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    vendor_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='purchase_order_vendor_rel',
        column1='purchase_order_id',
        column2='partner_id',
        string='Vendors',
        help='Select multiple vendors this RFQ should be sent to.',
    )
    bid_ids = fields.One2many(
        comodel_name='purchase.bid',
        inverse_name='purchase_order_id',
        string='Bids',
        help='Bids received from vendors against this RFQ.',
    )

    def action_rfq_send(self, force_send=False):
        """Extend the default 'Send RFQ' action so the email composer
        also includes every vendor in vendor_ids as a recipient,
        not just the primary Vendor (partner_id)."""
        res = super().action_rfq_send(force_send=force_send)
        if isinstance(res, dict) and res.get('context'):
            extra_partner_ids = self.vendor_ids.ids
            if extra_partner_ids:
                ctx = dict(res['context'])
                existing = ctx.get('default_partner_ids', [])
                ctx['default_partner_ids'] = list(set(existing) | set(extra_partner_ids))
                res['context'] = ctx
        return res
