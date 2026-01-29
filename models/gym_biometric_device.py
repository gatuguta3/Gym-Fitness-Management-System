from odoo import fields, models , api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta



class GymBiometricDevice(models.Model):
    _name = 'gym.biometric.device'
    _description = 'Gym Biometric Device'