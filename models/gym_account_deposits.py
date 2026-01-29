from odoo import fields, models , api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta



class GymAccountDeposits(models.Model):
    _name = 'gym.account.deposits'
    _description = 'Gym Account deposits'