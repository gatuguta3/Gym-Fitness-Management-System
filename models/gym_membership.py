from odoo import fields, models


class GymMembership(models.Model):
    _name = 'gym.membership'
    _description = 'Gym Membership'

    name = fields.Char(string='Membership Name', required=True)
    product_id = fields.Many2one('product.product', string='Membership Product', required=True)
    price = fields.Float(string='Price', required=True)
    time_frame=fields.Selection([
        ('days', 'Days'),
        ('months', 'Months')        
    ], string='Time Frame', required=True)
    duration = fields.Integer(string='Duration', required=True)
