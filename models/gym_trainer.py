import re
from odoo import models, fields, api


class GymTrainer(models.Model):
    _name = 'gym.trainer'
    _description = 'Gym Trainer'

    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    specialization = fields.Selection([
        ('gym trainer', 'Gym Trainer'),
        ('fitness trainer', 'Fitness Trainer'),
        ('crossfit trainer', 'Crossfit Trainer'),
        ('yoga trainer', 'Yoga Trainer')
    ], string='Specialization')
    member_ids = fields.Many2many('gym.member', string='Members')

    @api.constrains('email')
    def _check_email(self):
        email_pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        for record in self:
            if record.email and not email_pattern.match(record.email):
                raise models.ValidationError(
                    f"The email '{record.email}' is not valid. Please provide a correct email address.")

    def _capitalize_name(self):
        for record in self:
            if record.name:
                record.name = record.name[0].upper() + record.name[1:]

    @api.model
    def create(self, vals):
        if 'name' in vals and vals['name']:
            vals['name'] = vals['name'][0].upper() + vals['name'][1:]
        return super(GymTrainer, self).create(vals)

    def write(self, vals):
        if 'name' in vals and vals['name']:
            vals['name'] = vals['name'][0].upper() + vals['name'][1:]
        return super(GymTrainer, self).write(vals)

   
