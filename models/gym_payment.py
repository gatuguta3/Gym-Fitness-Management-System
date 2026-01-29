from odoo import fields, models, api
from odoo.exceptions import UserError


class GymPayment(models.Model):
    _name = 'gym.payment'
    _description = 'Gym Payment'

    member_id = fields.Many2one('gym.member', string='Member', required=True)
    membership_id = fields.Many2one('gym.membership', string='Membership', compute='_compute_membership', store=True)
    amount = fields.Float(string='Amount', required=True)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today)
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('mpesa', 'M-Pesa'),
        ('bank_transfer', 'Bank Transfer')
    ], string='Payment Method', required=True)
    status = fields.Selection([
        ('pending', 'Pending'),
        ('paid', 'Paid')
    ], string='Status', default='pending')

    @api.depends('member_id')
    def _compute_membership(self):
        for payment in self:
            if payment.member_id:
                payment.membership_id = payment.member_id.membership_id

    @api.onchange('membership_id')
    def _onchange_membership_id(self):
        if self.membership_id:
            self.amount = self.membership_id.price

    @api.onchange(amount)
    def _onchange_methods(self):
        if self.amount < 0:
            raise UserError('Negative numbers are not accepted!!')
