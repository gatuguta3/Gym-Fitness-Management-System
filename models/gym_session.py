from odoo import models, fields, api
from odoo.exceptions import ValidationError

class GymSession(models.Model):
    _name = 'gym.session'
    _description = 'Gym Session'
    _order = 'session_date desc'

    session_id = fields.Char(string='Session ID', required=True, readonly=True, copy=False, default='New')
    name = fields.Char(string='Session Name', required=True)
    session_date = fields.Date(string='Date', default=fields.Date.today, required=True)
    start_time = fields.Datetime(string='Start Time', default=fields.Datetime.now, required=True)
    close_time = fields.Datetime(string='Close Time')
    session_status = fields.Selection([
        ('active', 'Active'),
        ('closed', 'Closed')
    ], string='Status', default='active', readonly=False)
    
    # One session can have many attendance records
    attendance_ids = fields.One2many('gym.attendance', 'session_id', string='Attending Members')
    
    # Count fields for easy viewing
    members_count = fields.Integer(string='Members Count', compute='_compute_members_count')
    active_members_count = fields.Integer(string='Checked In', compute='_compute_members_count')
    
    @api.depends('attendance_ids', 'attendance_ids.status')
    def _compute_members_count(self):
        for record in self:
            record.members_count = len(record.attendance_ids)
            record.active_members_count = len(record.attendance_ids.filtered(lambda a: a.status == 'checked_in'))
    
    @api.model
    def create(self, vals):
        if vals.get('session_id', 'New') == 'New':
            vals['session_id'] = self.env['ir.sequence'].next_by_code('gym.session') or 'New'
        return super(GymSession, self).create(vals)
    
    def action_close_session(self):
        for record in self:
            # Check out all members who are still checked in
            active_attendances = record.attendance_ids.filtered(lambda a: a.status == 'checked_in')
            active_attendances.action_check_out()
            
            record.write({
                'close_time': fields.Datetime.now(),
                'session_status': 'closed'
            })