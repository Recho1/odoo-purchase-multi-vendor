from odoo import models, fields, api
from odoo.exceptions import UserError


class PurchaseBid(models.Model):
    _name = 'purchase.bid'
    _description = 'Vendor Bid on an RFQ'
    _order = 'price asc'

    purchase_order_id = fields.Many2one(
        comodel_name='purchase.order',
        string='RFQ',
        required=True,
        ondelete='cascade',
        help='The Request for Quotation this bid was submitted against.',
    )
    vendor_id = fields.Many2one(
        comodel_name='res.partner',
        string='Vendor',
        required=True,
        help='The vendor who submitted this bid.',
    )
    price = fields.Monetary(
        string='Bid Price',
        required=True,
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        related='purchase_order_id.currency_id',
        store=True,
        readonly=True,
    )
    notes = fields.Text(string='Notes')
    is_winner = fields.Boolean(
        string='Winning Bid',
        default=False,
        readonly=True,
        help='Marked automatically when this bid is selected as the winner.',
    )
    state = fields.Selection(
        selection=[
            ('submitted', 'Submitted'),
            ('won', 'Won'),
            ('lost', 'Lost'),
        ],
        string='Status',
        default='submitted',
        readonly=True,
    )

    def action_select_as_winner(self):
        """Mark this bid as the winner, mark all sibling bids on the same
        RFQ as lost, and generate/confirm a Purchase Order for the winning
        vendor."""
        self.ensure_one()
        if self.state == 'won':
            raise UserError("This bid has already been selected as the winner.")

        sibling_bids = self.purchase_order_id.bid_ids
        sibling_bids.write({'is_winner': False, 'state': 'lost'})
        self.write({'is_winner': True, 'state': 'won'})

        po = self.purchase_order_id
        po.write({
            'partner_id': self.vendor_id.id,
        })
        for line in po.order_line:
            line.price_unit = self.price if len(po.order_line) == 1 else line.price_unit

        po.button_confirm()
        return True
