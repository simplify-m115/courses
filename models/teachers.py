import random

from odoo import api, fields, models

import passlib.context


class Teachers(models.Model):
    _name = "courses.teachers"
    _description = "Teachers"

    name = fields.Char(string='Teacher name', required=True)
    teacher_surname = fields.Char(string='Teacher surname', required=True)
    teacher_email = fields.Char(string='Teacher email', required=True)

    teacher_courses = fields.One2many(
        'courses.courses',
        'course_teacher_name',
        string="Courses",
        required=False,
        readonly=True)

    teacher_access = fields.Many2one(
        'res.partner')

    teacher_classroom = fields.Integer(
        string="Teachers class room.",
        required=True
    )

    def name_get(self):
        name = []
        for record in self:
            name.append((
                record.id, record.name +
                ' ' + record.teacher_surname
            ))
        return name



    @api.model
    def create(self, vals):
        rec = super(Teachers, self).create(vals)

        contact_data = {
            'name': rec.name,
            'email': rec.teacher_email
        }
        contact = self.env['res.partner'].create(contact_data)

        if contact:
            rec.write({'teacher_access': contact.id})
            user = self.env['res.users'].sudo().create({'partner_id': contact.id, 'login': contact.email})
            crypt_context = passlib.context.CryptContext(["pbkdf2_sha512", "hex_md5", "plaintext"],
            deprecated=["hex_md5", "plaintext"])
            hashed_password = crypt_context.hash('admin')
            self.env['res.users']._set_encrypted_password(user.id, hashed_password)
            group_portal = self.env.ref('base.group_portal')
            #user.write({'groups_id': [(4, group_portal.id)]})
            user.write({'groups_id': [(6, 0, [group_portal.id])]})

        return rec

    def send_mail(self):
        print("mail sent")
        template_id = self.env.ref('courses.send_student_mail_template').id
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)
