from odoo import fields, models, api
from odoo.exceptions import ValidationError

class GymEquipment(models.Model):
    _name='gym.equipment'
    _description='Gym Equipment'

    """
    all fields of the above model go here
    they may include    name,category,image,quantity
    for categories there are   (weights,machines,spin bikes , barbells , )
    """

    name = fields.Char(string='Name', required=True)
    description = fields.Char(string='Description', required=True)
    category = fields.Selection([
        ('weights', 'Weights'),
        ('machines', 'Machines'),
        ('spin bikes', 'Spin Bikes'),
        ('barbells', 'Barbells'),
        ('others', 'Others')], string='Category', required=True)
    quantity=fields.Integer(string='Quantity', required=True)
    image = fields.Binary(string='Equipment Image', attachment=True)

    @api.constrains('quantity')
    def _check_quantity(self):
        """Validate that quantity is not negative"""
        for record in self:
            if record.quantity < 0:
                raise ValidationError("Quantity cannot be negative!")

    