from odoo import api, fields, models
from datetime import datetime
import re
from odoo.exceptions import ValidationError
import passlib.context


class Students(models.Model):
    _name = "courses.students"
    _description = "Students"

    student_name = fields.Char(string='Students name', required=True)

    student_surname = fields.Char(string='Students surname', required=True)

    student_email = fields.Char(string='Students email', required=True)

    student_enrolled_year = fields.Selection(
        [(str(year), str(year))
         for year in range(datetime.now().year - 1, datetime.now().year + 1)],
    string="Enrolled year", required=True)

    student_birth_date = fields.Date(string="Student birth date", required=True)

    student_index_number = fields.Char(
        string = "Index number", default="/", readonly=True)

    student_field_of_study = fields.Text(
        string="Field of study", required=True)

    student_access = fields.Many2one(
        'res.partner')

    student_grades = fields.One2many(
        'courses.grades',
        'student'
    )

    @api.constrains('student_index_number')
    def _check_change_enrolled_year(self):
        for record in self:
            if record.student_index_number == '/':
                record.student_index_number = str(record.id) + "/" + record.student_enrolled_year
            else:
                index_number = record.student_index_number
                enrollment_year = record.student_enrolled_year
                if index_number.split('/')[1] != enrollment_year:
                    record.student_index_number = str(index_number.split('/')[0]) + '/' + enrollment_year


    # def unlink(self):
    #     for record in self:
    #         if record.student_grades:
    #             grades = record.student_grades
    #
    #             for i in range(0, len(grades)):
    #                 course = record.env["courses.courses"] \
    #                     .search([('id', '=', grades[i].course.id)])
    #                 course.number_students_in_course -= 1
    #
    #     return super(Students, self).unlink()

    def name_get(self):
        name = []
        for record in self:
            name.append((
                record.id,
                record.student_name + ' ' +
                record.student_surname + ' ' +
                record.student_index_number))
        return name

    @api.model
    def create(self, vals):
        rec = super(Students, self).create(vals)

        contact_data = {
            'name': rec.student_name,
            'email': rec.student_email
        }
        contact = self.env['res.partner'].create(contact_data)

        if contact:
            rec.write({'student_access': contact.id})
            user = self.env['res.users'].sudo().create({'partner_id': contact.id, 'login': contact.email})
            crypt_context = passlib.context.CryptContext(["pbkdf2_sha512", "hex_md5", "plaintext"],
                                                         deprecated=["hex_md5", "plaintext"])
            hashed_password = crypt_context.hash('admin')
            self.env['res.users']._set_encrypted_password(user.id, hashed_password)
            group_portal = self.env.ref('base.group_portal')
            # user.write({'groups_id': [(4, group_portal.id)]})
            user.write({'groups_id': [(6, 0, [group_portal.id])]})

        return rec