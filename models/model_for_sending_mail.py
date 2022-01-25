from odoo import models, fields, api


class SendMailModel(models.TransientModel):
    _name = 'courses.send_mail'
    _description = "Course Send Mail"

    teacher = fields.Many2one('courses.teachers', string='Teacher', required=True)
    student = fields.Many2one('courses.students', string='Student', required=True)
    course = fields.Many2one('courses.courses', string='Course', required=True)

    def send_welcome_mail(self):
        self.ensure_one()
        template_id = self.env.ref('courses.send_student_mail_template').id
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)
