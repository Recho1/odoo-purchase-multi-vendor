from odoo import models, fields, api
from odoo.exceptions import UserError


class PurchaseRequest(models.Model):
    _name = 'purchase.request'
    _description = 'Purchase Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Reference',
        default='New',
        readonly=True,
        copy=False,
    )
    employee_id = fields.Many2one(
        comodel_name='res.users',
        string='Requested By',
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
    )
    description = fields.Char(
        string='Description',
        required=True,
        help='What is being requested.',
    )
    line_ids = fields.One2many(
        comodel_name='purchase.request.line',
        inverse_name='request_id',
        string='Products',
    )
    justification = fields.Text(string='Justification')
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('converted', 'Converted to RFQ'),
        ],
        string='Status',
        default='draft',
        required=True,
        copy=False,
        tracking=True,
    )
    purchase_order_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Related RFQ',
        readonly=True,
        copy=False,
        help='The RFQ generated from this request, once converted.',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('purchase.request') or 'New'
        return super().create(vals_list)

    def action_submit(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError('Add at least one product line before submitting.')
        self.write({'state': 'submitted'})

    def action_approve(self):
        for rec in self:
            if rec.employee_id == self.env.user:
                raise UserError('You cannot approve your own request.')
        self.write({'state': 'approved'})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})

    def action_convert_to_rfq(self):
        """Create a draft RFQ (purchase.order) from this approved request,
        so Procurement can then assign vendors and send it out.
        """
        self.ensure_one()
        if self.state != 'approved':
            raise UserError('Only approved requests can be converted to an RFQ.')

        placeholder_vendor = self.env['res.partner'].search(
            [('supplier_rank', '>', 0)], limit=1
        )
        if not placeholder_vendor:
            placeholder_vendor = self.env['res.partner'].search([], limit=1)
        if not placeholder_vendor:
            raise UserError(
                'No vendor contacts exist in the system. Please create at '
                'least one vendor contact before converting requests to an RFQ.'
            )

        order_vals = {
            'origin': self.name,
            'partner_id': placeholder_vendor.id,
            'order_line': [(0, 0, {
                'product_id': line.product_id.id,
                'name': line.description or line.product_id.name,
                'product_qty': line.quantity,
                'product_uom_id': line.uom_id.id or line.product_id.uom_id.id,
                'price_unit': line.estimated_price,
                'date_planned': fields.Datetime.now(),
            }) for line in self.line_ids],
        }
        po = self.env['purchase.order'].create(order_vals)

        self.write({
            'state': 'converted',
            'purchase_order_id': po.id,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'res_id': po.id,
            'view_mode': 'form',
            'target': 'current',
        }
