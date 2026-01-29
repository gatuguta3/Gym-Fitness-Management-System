from datetime import date
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import re
import requests


class GymMember(models.Model):
    _name = 'gym.member'
    _description = 'Gym Member'

    profile_image = fields.Binary(string='Profile Image', attachment=True)
    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    age = fields.Integer(string='Age')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string='Gender')
    join_date = fields.Date(string='Join Date', default=fields.Date.today)
    expiry_date = fields.Date(string='Expiry Date', compute='_compute_expiry_date', store=True)
    membership_id = fields.Many2one('gym.membership', string='Membership')
    #membership_state = fields.Selection(related='membership_id.state', string='Membership State', store=True)
    last_renewal_date = fields.Date(string='Last Renewal Date')
    attendance_ids = fields.One2many('gym.attendance', 'member_id', string='Attendances')
    last_check_in = fields.Datetime(string='Last Check In', compute='_compute_last_check_in', store=True)
    amount_due=fields.Integer(string='Amount Due')
    payment_ids = fields.One2many('gym.payment', 'member_id', string='Payments')
    attendance_state = fields.Selection([
        ('inactive', 'Inactive'),
        ('active', 'Active')],
          default='active', 
          string="Attendance Status", 
          compute="check_attendance_status",
          )

    total_paid = fields.Integer(
        string='Total Paid', 
        compute='_compute_payment_totals', 
        store=True,
        help='Total amount paid by the member'
    )


    amount_due_ = fields.Integer(
        string='Amount Due', 
        compute='_compute_remaining_amount', 
        store=True,
        help='Amount still due after payments'
    )

    membership_state = fields.Selection([
            ('renewed' , 'Renewed'),
            ('expired' , 'Expired')
        ], 
        default='expired',
        string="Membership Status", 
        compute="check_membership_status",
        help="Indicates whether the membership is renewed or expired based on payments and dates."
    )

    unpaid_dues=fields.Integer(string='Past Dues', compute='_compute_remaining_amount', store=True)

    #Remaining functions
        # Send automatic reminders of renewals
        #Automatic renewal will be done once the member attends the gym  after the expiry of membership

    
    def action_renew_membership(self):
        """Procedure to renew membership automatically if conditions are met"""
        today = date.today()
        amount_due = self.amount_due

        for member in self:
            if member.membership_state == 'expired' and member.amount_due > 0:
                # Renew membership
                member.last_renewal_date = today
                member._compute_expiry_date()  # Recompute expiry date
                amount_due = amount_due
                return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error message',
                    'message': f' Membership renewal is unsuccessful for {member.name},  because they have an outstanding amount of Ksh {amount_due}!',
                    'type': 'warning',
                    'sticky': True,
                }
            }
            else:
                member.last_renewal_date = today
                member._compute_expiry_date()  # Recompute expiry date
                amount_due = member.membership_id.price
                member.membership_state = 'renewed'
                
        return True


    @api.depends('payment_ids.amount', 'amount_due')
    def _compute_payment_totals(self):
        """Compute total paid amount and remaining amount due"""
        for member in self:
            # Calculate total paid amount from all payments
            # Remove the state filter if your payment model doesn't have a state field';
                    
            total_paid = sum(member.payment_ids.mapped('amount'))
            
            member.total_paid = total_paid


    # And a method to check if membership is active
    def check_attendance_status(self):
        """Check and update membership status"""
        today = date.today()
        for member in self:
            
            last_check_in_date = member.last_check_in.date()
            days_since_last_attendance = (today - last_check_in_date).days
            
            if days_since_last_attendance >= 30:
                # Last attendance was 40+ days ago - mark as inactive
                member.attendance_state = 'inactive'
             # Skip other checks since we've already set to inactive
            else:
                member.attendance_state = 'active'


    # Compute membership state with payment validation and expiry date
    @api.depends('expiry_date')
    def check_membership_status(self):
        """Compute membership state with payment validation"""
        today = date.today()
        
        for member in self:            
            
            days_past_expiry = (today - member.expiry_date).days
            # Check if expired by date
            if days_past_expiry > 0 :
                member.membership_state = 'expired'
            else:
                # Default state if dates are not set
                member.membership_state = 'renewed'

   


# All message functions start from here
# Twilio and other gateway integrations can be added later

    def action_send_payment_remainder(self):
        """Send payment due reminders to members via SMS"""   
        url = "{{SERVER}}/send"     
        
        for member in self:

            message = f"Dear {member.name}, you have an outstanding amount of Ksh {member.amount_due}. Please make the payment at your earliest convenience. Thank you!"
            

            payload = { 'userid': '{{USER_ID}}',
                        'password': '{{PASSWORD}}',
                        'mobile': member.phone,
                        'senderid': '{{SENDER_NAME}}',
                        'msg': message,
                        'sendMethod': 'quick',
                        'msgType': 'text',
                        'output': 'json',
                        'duplicatecheck': 'true'
                      }
            files=[

            ]
            headers = {}
            if member.phone and member.amount_due > 0:
                    
            # Show notification
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'SMS Sent',
                        'message': f'Payment reminder prepared for {member.name}: {message}',
                        'type': 'success',
                        'sticky': False,
                    }
                }
        return True

    
    @api.depends('fingerprint_id')
    def _compute_fingerprint_enrolled(self):
        for record in self:
            record.fingerprint_enrolled = bool(record.fingerprint_id)

    @api.constrains('email')
    def _check_email(self):
        email_pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        for record in self:
            if record.email and not email_pattern.match(record.email):
                raise ValidationError(
                    f"The email '{record.email}' is not valid. Please provide a correct email address."
                )

    @api.constrains('phone')
    def _check_phone(self):
        for record in self:
            if record.phone and not record.phone.isdigit():
                raise ValidationError('Phone number should contain only digits.')
            if len(record.phone) != 10:
                raise ValidationError('Phone number should be exactly 10 digits long.')

    @api.constrains('age')
    def _check_age(self):
        for record in self:
            if record.age < 17:
                raise ValidationError('Members under 17 years old cannot join the gym.')



    @api.depends('join_date', 'membership_id', 'last_renewal_date', 'attendance_state')
    def _compute_expiry_date(self):
        """Compute expiry date based on membership duration"""
        today = fields.Date.today()
        
        for record in self:
            # Only compute for active members
            if record.attendance_state != 'active':
                record.expiry_date = False
                continue
            
            # Check if we have a valid membership
            if not record.membership_id:
                record.expiry_date = False
                continue
            
            membership = record.membership_id
            
            # Validate required fields
            if not membership.duration:
                record.expiry_date = False
                continue
            
            if not membership.time_frame:
                # Default to months if not specified
                time_frame = 'months'
            else:
                time_frame = membership.time_frame
            
            # Ensure duration is positive
            if membership.duration <= 0:
                record.expiry_date = False
                continue
            
            # Determine reference date for calculation
            reference_date = None
            
            # CASE 1: Use last_renewal_date if it exists (highest priority)
            if record.last_renewal_date:
                reference_date = record.last_renewal_date
            
            # CASE 2: No last_renewal_date but has join_date
            elif record.join_date:
                reference_date = record.join_date
            
            # CASE 3: No reference dates available
            else:
                reference_date = today
            
            # Check if we need to recalculate based on existing expiry date
            if record.expiry_date:
                # If existing expiry date is in the future and last_renewal_date hasn't changed,
                # we might not want to recalculate. This depends on your business logic.
                
                # If you want to always recalculate when last_renewal_date changes:
                # The @api.depends decorator already handles this - it will trigger computation
                # when last_renewal_date changes, so we should calculate new expiry
                
                # If existing expiry date is in the past, definitely recalculate
                if record.expiry_date >= today:
                    # Optional: Skip if last_renewal_date hasn't changed and expiry is still valid
                    # This prevents unnecessary recalculations
                    continue
            
            # Calculate new expiry date based on time frame
            try:
                if time_frame == 'days':
                    record.expiry_date = reference_date + relativedelta(days=membership.duration)
                elif time_frame == 'months':
                    record.expiry_date = reference_date + relativedelta(months=membership.duration)
                elif time_frame == 'years':  # Optional: add years support
                    record.expiry_date = reference_date + relativedelta(years=membership.duration)
                else:
                    # Invalid time frame
                    raise ValueError(f"Invalid time_frame value: '{time_frame}'")
                    
                print(f"SUCCESS: Calculated expiry date {record.expiry_date} from reference {reference_date} with {membership.duration} {time_frame}")
                    
            except Exception as e:
                print(f"ERROR calculating expiry date: {e}")
                record.expiry_date = False
        



    @api.depends('membership_id.price', 'payment_ids.amount', 'payment_ids.status','payment_ids.payment_date')
    def _compute_remaining_amount(self):
        """Compute remaining amount based on membership price and payments"""
        for member in self:
            remaining = 0
            if member.membership_id and member.membership_id.price:
                total_due = member.membership_id.price
                
                # Get all confirmed/done payments between last renewal date and expiration date
                
                valid_payments = member.payment_ids.filtered(
                    lambda p: (
                        p.status in ['paid', 'Paid'] 
                        and p.payment_date >= member.last_renewal_date 
                        and p.payment_date <= member.expiry_date
                    )
                )

                total_paid = sum(valid_payments.mapped('amount'))
                remaining = max(0, total_due - total_paid)
                
            member.amount_due = remaining
   
   
    def action_extend_membership(self):
        """Open wizard to input extension duration"""
        self.ensure_one()  # Ensure only one record is selected
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Extend Membership: {self.name}',
            'res_model': 'membership.extension.wizard',
            'view_mode': 'form',
            'target': 'new',  # This makes it a popup window
            'context': {
                'default_member_id': self.id,
                'default_member_name': self.name,
                'default_current_expiry': self.expiry_date,
                'active_id': self.id,  # Important for default_get in wizard
            }
        }

    @api.depends('attendance_ids.check_in')
    def _compute_last_check_in(self):
        for member in self:
            last_attendance = self.env['gym.attendance'].search([
                ('member_id', '=', member.id),
                ('status', '=', 'checked_in')
            ], limit=1, order='check_in desc')
            member.last_check_in = last_attendance.check_in if last_attendance else False

    
    def _capitalize_name(self):
        for record in self:
            if record.name:
                record.name = record.name[0].upper() + record.name[1:]

    @api.model
    def create(self, vals):
        if 'name' in vals and vals['name']:
            vals['name'] = vals['name'][0].upper() + vals['name'][1:]
        return super(GymMember, self).create(vals)

    def write(self, vals):
        if 'name' in vals and vals['name']:
            vals['name'] = vals['name'][0].upper() + vals['name'][1:]
        return super(GymMember, self).write(vals)

