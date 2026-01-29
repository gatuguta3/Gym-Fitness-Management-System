from odoo import models, fields, api


class GymReport(models.Model):
    _name = 'gym.report'
    _description = 'Gym Report'

    name = fields.Char(string='Report Name', required=True)
    report_type = fields.Selection([
        ('member', 'Member Report'),
        ('trainer', 'Trainer Report'),
        ('payment', 'Payment Report'),
        ('attendance', 'Attendance Report'),
        ('activity', 'Activity Report')
    ], string='Report Type', required=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    data = fields.Text(string='Report Data', compute='_compute_data', store=True)

    @api.depends('report_type', 'start_date', 'end_date')
    def _compute_data(self):
        for report in self:
            if report.report_type == 'member':
                report.data = self._generate_member_report(report.start_date, report.end_date)
            elif report.report_type == 'trainer':
                report.data = self._generate_trainer_report(report.start_date, report.end_date)
            elif report.report_type == 'payment':
                report.data = self._generate_payment_report(report.start_date, report.end_date)
            elif report.report_type == 'attendance':
                report.data = self._generate_attendance_report(report.start_date, report.end_date)
            elif report.report_type == 'activity':
                report.data = self._generate_activity_report(report.start_date, report.end_date)

    def _generate_member_report(self, start_date, end_date):
        members = self.env['gym.member'].search([
            ('join_date', '>=', start_date),
            ('join_date', '<=', end_date)
        ])
        report_data = "Member Report:\n"
        for member in members:
            report_data += f"Name: {member.name}, Email: {member.email}, Phone: {member.phone}, Join Date: {member.join_date}\n"
        return report_data

    def _generate_trainer_report(self, start_date, end_date):
        trainers = self.env['gym.trainer'].search([
            ('hire_date', '>=', start_date),
            ('hire_date', '<=', end_date)
        ])
        report_data = "Trainer Report:\n"
        for trainer in trainers:
            report_data += f"Name: {trainer.name}, Email: {trainer.email}, Phone: {trainer.phone}, Hire Date: {trainer.hire_date}\n"
        return report_data

    def _generate_payment_report(self, start_date, end_date):
        payments = self.env['gym.payment'].search([
            ('payment_date', '>=', start_date),
            ('payment_date', '<=', end_date)
        ])
        report_data = "Payment Report:\n"
        for payment in payments:
            report_data += f"Member: {payment.member_id.name}, Amount: {payment.amount}, Payment Date: {payment.payment_date}, Method: {payment.payment_method}\n"
        return report_data

    def _generate_attendance_report(self, start_date, end_date):
        attendances = self.env['gym.attendance'].search([
            ('check_in', '>=', start_date),
            ('check_in', '<=', end_date)
        ])
        report_data = "Attendance Report:\n"
        for attendance in attendances:
            report_data += f"Member: {attendance.member_id.name}, Check In: {attendance.check_in}, Check Out: {attendance.check_out}\n"
        return report_data

    def _generate_activity_report(self, start_date, end_date):
        activities = self.env['gym.activity'].search([
            ('activity_date', '>=', start_date),
            ('activity_date', '<=', end_date)
        ])
        report_data = "Activity Report:\n"
        for activity in activities:
            report_data += f"Activity: {activity.name}, Date: {activity.activity_date}, Trainer: {activity.trainer_id.name}, Members: {', '.join(member.name for member in activity.member_ids)}\n"
        return report_data
