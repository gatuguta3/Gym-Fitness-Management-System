from odoo import fields, models , api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta



class GymAcccount(models.Model):
    _name = 'gym.account'
    _description = 'Gym Accounts'

    name = fields.Char(string='Account Name', required=True)
    acc_no= fields.Char(string='Account Number', required=True, unique=True)
    account_type = fields.Selection([
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('income', 'Income'),
        ('expense', 'Expense'),
    ], string='Account Type', required=True)
    balance = fields.Float(string='Balance', default=0.0)