from odoo import fields, models , api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta



class GymActivity(models.Model):
    _name = 'gym.activity'
    _description = 'Gym Activity'

    name = fields.Selection([
        ('fitness', 'Fitness Class'),
        ('yoga', 'Yoga Class'),
        ('spin', 'Spin Class'),
        ('taebo', 'Taebo Class'),
        ('Crossfit', 'CrossFit Class')
    ], string='Name', required=True)
    trainer_id = fields.Many2one('gym.trainer', string='Trainer', required=True)
    duration = fields.Float(string='Duration (hours)')
    date = fields.Date(string='Date')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'Progress'),
        ('done', 'Finished'),
        ('cancel', 'Cancelled')], default='draft', string="Status", required=True)
    member_id = fields.Many2many('gym.member', string='Attending Member')

   
    
    
    @api.onchange('start_time', 'duration')
    def _compute_end_time(self):
        """Compute end_time based on start_time and duration"""
        for record in self:
            if record.start_time and record.duration:
                # Convert duration from hours to minutes for timedelta
                duration_minutes = record.duration * 60
                record.end_time = record.start_time + timedelta(minutes=duration_minutes)
            else:
                record.end_time = False

    @api.constrains('start_time', 'duration')
    def _check_valid_times(self):
        """Validate that end_time is after start_time"""
        for record in self:
            if record.start_time and record.duration and record.duration <= 0:
                raise ValidationError("Duration must be greater than 0 hours")
            if record.start_time and record.end_time and record.end_time <= record.start_time:
                raise ValidationError("End time must be after start time")
            

    def update_activity_states(self):
        """Update activity states based on current time"""
        now = datetime.now()
        
        # Find activities that should be in progress
        activities_to_start = self.search([
            ('state', 'in', ['draft']),
            ('start_time', '<=', now),
            ('end_time', '>', now)
        ])
        
        if activities_to_start:
            activities_to_start.write({'state': 'progress'})
        
        # Find activities that should be finished
        activities_to_finish = self.search([
            ('state', 'in', ['draft', 'progress']),
            ('end_time', '<=', now)
        ])
        
        if activities_to_finish:
            activities_to_finish.write({'state': 'done'})
        
        return True

    def action_start_activity(self):
        """Manual action to start activity"""
        for record in self:
            if record.state == 'draft':
                record.state = 'progress'
    
    def action_end_activity(self):
        """Manual action to end activity"""
        for record in self:
            if record.state == 'progress':
                record.state = 'done'


    def action_share_whatsapp(self):
        if not self.trainer_id.phone:
            raise ValidationError("Missing phone number in trainer record")
        
        message = 'Hi *%s*, your next *activity* is on: %s. Thank you!' % (self.trainer_id.name, self.start_time)
        
        from twilio.rest import Client
        
        # Twilio configuration
        account_sid = 'AC342ff76e27518fee1d660d41fdf80a9c'
        auth_token = '4f4912a45bbdb718841e4520fbdbf8c4'
        client = Client(account_sid, auth_token)
        
        try:
            message = client.messages.create(
                from_='whatsapp:+12769001255',  # Twilio WhatsApp number
                body=message,
                to=f'whatsapp:{self.trainer_id.phone}'
            )
            
            # Success notification
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': f'WhatsApp message sent! SID: {message.sid}',
                    'type': 'success',
                }
            }
        except Exception as e:
            raise ValidationError(f"Failed to send WhatsApp message: {str(e)}")