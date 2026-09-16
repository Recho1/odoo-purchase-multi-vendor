from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PurchaseRequestLine(models.Model):
    _name = 'purchase.request.line'
    _description = 'Purchase Request Line'

    request_id = fields.Many2one(
        comodel_name='purchase.request',
        string='Request',
        required=True,
        ondelete='cascade',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True,
    )
    description = fields.Char(string='Description')
    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    uom_id = fields.Many2one(comodel_name='uom.uom', string='UoM')
    estimated_price = fields.Float(string='Estimated Unit Price')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.display_name
            self.uom_id = self.product_id.uom_id
            self.estimated_price = self.product_id.standard_price

    @api.constrains('quantity')
    def _check_quantity_positive(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError('Quantity must be greater than zero.')

    @api.constrains('estimated_price')
    def _check_price_not_negative(self):
        for line in self:
            if line.estimated_price < 0:
                raise ValidationError('Estimated price cannot be negative.')
