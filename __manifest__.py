{
    'name': 'Izone Fitness Center',
    'sequence': 1,
    'version': '1.0',
    'summary': 'Subscription management system for Izon fitness center',
    'description': 'A comprehensive gym management system to manage members, trainers, activities, attendance, payments, and equipment for Izon Fitness Center. Well integrated with a website for  Customers to get information regarding trainers , classes and events to be held by the gym',
    'category': 'Gym management',
    'author': 'Joseph Gatuguta',
    'website': 'Website',
    'depends': ['base', 'mail', 'calendar', 'sale'],
    'data': [
        
        'views/gym_menus.xml',  
        'views/gym_member_views.xml',
        'views/gym_activity_views.xml',
        'views/gym_attendance_views.xml',
        'views/gym_membership_views.xml',
        'views/gym_trainer_views.xml',
        'views/gym_payment_views.xml',
        'views/gym_account_view.xml',        
        'views/gym_report_views.xml',
        'views/gym_equipment_views.xml',   
        'views/gym_session_views.xml',         
        'data/email_template_data.xml',
        'data/sequences.xml',  
        'security/gym_security.xml',
        'security/ir.model.access.csv'                
         
        
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
