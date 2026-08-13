from odoo import models, fields, api


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

    @api.onchange('vendor_ids')
    def _onchange_vendor_ids(self):
        """Convenience: if the primary Vendor field is empty, default it to
        the first vendor selected in the Vendors list, so the user usually
        only needs to interact with one field."""
        if self.vendor_ids and not self.partner_id:
            self.partner_id = self.vendor_ids[0]

    def action_rfq_send(self, *args, **kwargs):
        """Extend the default 'Send RFQ' action so the email composer
        also includes every vendor in vendor_ids as a recipient,
        not just the primary Vendor (partner_id).

        Accepts *args/**kwargs rather than a fixed signature since the
        core method's exact parameters vary between Odoo versions."""
        res = super().action_rfq_send(*args, **kwargs)
        if isinstance(res, dict) and res.get('context'):
            extra_partner_ids = self.vendor_ids.ids
            if extra_partner_ids:
                ctx = dict(res['context'])
                existing = ctx.get('default_partner_ids', [])
                ctx['default_partner_ids'] = list(set(existing) | set(extra_partner_ids))
                res['context'] = ctx
        return res
