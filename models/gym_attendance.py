from odoo import models, fields, api
from odoo.exceptions import ValidationError

class GymAttendance(models.Model):
    _name = 'gym.attendance'
    _description = 'Gym Attendance'
    _order = 'check_in desc'

    # Link to the session
    session_id = fields.Many2one('gym.session', string='Session', required=True, ondelete='cascade')
    
    # Member information
    member_id = fields.Many2one('gym.member', string='Member', required=True)
    check_in = fields.Datetime(string='Check In', default=fields.Datetime.now)
    check_out = fields.Datetime(string='Check Out')
    status = fields.Selection([
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out')
    ], string='Status', default='checked_in', readonly=True)

    @api.constrains('member_id', 'session_id')
    def _check_unique_member_per_session(self):
        for record in self:
            if record.session_id and record.member_id:
                existing = self.search([
                    ('session_id', '=', record.session_id.id),
                    ('member_id', '=', record.member_id.id),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(f'Member {record.member_id.name} is already in this session.')

    @api.constrains('check_in', 'check_out')
    def _check_check_out_after_check_in(self):
        for record in self:
            if record.check_out and record.check_out < record.check_in:
                raise ValidationError('Check-out time must be after check-in time.')

    def action_check_out(self):
        for record in self:
            if record.status == 'checked_out':
                raise ValidationError('This member is already checked out.')
            record.write({
                'check_out': fields.Datetime.now(),
                'status': 'checked_out'
            })
    
    def action_check_in(self):
        for record in self:
            if record.status == 'checked_in':
                raise ValidationError('This member is already checked in.')
            record.write({
                'check_in': fields.Datetime.now(),
                'status': 'checked_in',
                'check_out': False
            })