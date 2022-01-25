from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Courses(models.Model):
    _name = 'courses.courses'
    _description = 'Courses'

    course_teacher_name = fields.Many2one(
        "courses.teachers",
        ondelete="cascade",
        string="Teacher of this course",
        help="Teacher that teaches this course.",
        required=False)
    name = fields.Char(
        string="Course name",
        help="Name of the course.",
        required=True)
    course_field_of_study = fields.Text(
        string="Field of study",
        help="Field of study of the course.",
        required=True)
    course_semester = fields.Selection(
        [('1st Semester', '1st Semester'),
         ('2nd Semester', '2nd Semester'),
         ('3rd Semester', '3rd Semester'),
         ('4th Semester', '4th Semester'),
         ('5th Semester', '5th Semester'),
         ('6th Semester', '6th Semester'),
         ('7th Semester', '7th Semester'),
         ('8th Semester', '8th Semester')],
        string="Semester",
        help="The course is studied in the # semester.",
        required=True)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('open', 'Open'),
         ('finished', 'Finished')],
        string='Course state',
        help="State of the course.",
        default='draft',
        required=True,
        readonly=True)

    course_description = fields.Text(
        string='Course description',
        help="Description of the course.",
        required=True)
    course_start_date = fields.Date(
        string="Start date of the course",
        help="Start date of the course.",
        required=True)
    course_end_date = fields.Date(
        string="End date of the course",
        help="End date of the course.",
        required=True)
    course_file = fields.Many2many(
        'ir.attachment',
        'class_ir_attachments_rel',
        'class_id',
        'attachment_id',
        string="Course material",
        help="Material of the course.",
        required=False)

    students_in_course = fields.Many2many(
        'courses.students',
        string="Students in the course",
        help="Students that are enrolled in the course.",
        required=False)

    student_grades = fields.One2many(
        'courses.grades',
        'course',
        string='Grades',
        required=False
    )

    number_students_in_course = fields.Integer(
        string="Number of students",
        help="Number of students enrolled"
             "in the course.")

    course_is_published = fields.Boolean(
        default=True,
        string="Published"
    )

    welcomed_students = fields.Char(
        string="ID's of students that are welcomed in course",
        default='{"students": []}',
        readonly=True
    )

    @api.model
    def create(self, vals):
        record = super(Courses, self).create(vals)
        product_data = {'name': record.name, 'list_price': 100, 'is_published': True}
        record.env['product.template'].create(product_data)
        return record

    def action_open(self):
        for record in self:
            record.state = "open"

    def action_draft(self):
        for record in self:
            if record.state == "open" or record.state == "finished":
                record.state = "draft"
            else:
                raise ValidationError(
                    "You're course has "
                    "to be in open state "
                    "in order to change the "
                    "state to Draft."
                )

    def grade_form(self):
        for record in self:
            form_name = ""

            if record.state == "open":
                form_name = "Insert Grades"
            elif record.state == "finished":
                form_name = "View Grades"

            view_id = record.env.ref('courses.insert_grades_form').id
            context = record._context.copy()

            return {
                'name': form_name,
                'view_type': 'form',
                'view_mode': 'tree',
                'views': [(view_id, 'form')],
                'res_model': 'courses.courses',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'res_id': record.id,
                'target': 'new',
                'context': context,
            }

    @api.constrains("students_in_course")
    def number_of_students(self):
        for record in self:
            record.number_students_in_course = len(record.students_in_course)

            student_grades = record.env["courses.grades"] \
                .search([('course', '=', record.id)])

            for i in range(0, len(student_grades)):
                flag = False
                for j in range(0, len(record.students_in_course)):
                    if student_grades[i].student.id == \
                            record.students_in_course[j].id:
                        flag = True
                        break

                if not flag:
                    student_grades[i].unlink()

            for i in range(0, len(record.students_in_course)):
                obj = record.env["courses.grades"].search([
                    ('course', '=', record.id),
                    ('student', '=', record.students_in_course[i].id)
                ])

                if not obj:
                    record.env["courses.grades"].create({
                        'course': record.id,
                        'student': record.students_in_course[i].id
                    })

    def copy_course(self, default=None):
        for record in self:

            if record.state == "finished":
                default = dict(default or {})
                default.update({
                    'students_in_course': None,
                    'student_grades': None,
                    'state': 'draft',
                    'number_students_in_course': None,
                })
                copy = super(Courses, record).copy(default)
                view_id = record.env.ref('courses.courses_form_view').id

                return {
                    'name': 'form_name',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'courses.courses',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'res_id': copy.id,
                    'target': 'current'
                }

            else:
                raise ValidationError(
                    "The state has to be finished "
                    "in order to make a copy of the "
                    "course."
                )

    def action_finished(self):
        for record in self:

            if record.state != "open":
                raise ValidationError(
                    "You're course has "
                    "to be in Open state "
                    "in order to change the "
                    "state to Finished."
                )

            student_grades = record.env["courses.grades"] \
                .search([('course', '=', record.id)])
            assigned_grades = 0

            for i in range(0, len(student_grades)):
                if student_grades[i].grade:
                    assigned_grades += 1

            if record.state == "open" and \
                    len(student_grades) == assigned_grades:
                record.state = "finished"

            else:
                raise ValidationError(
                    "You have not assigned a "
                    "grade for every student."
                )

    def name_get(self):
        name = []

        for record in self:
            name.append((
                record.id,
                record.name +
                ' (' + record.course_semester +
                f") ({record.state})"
            ))

        return name

    def print_report(self):
        return self.env.ref('courses.report_course_card').report_action(self)
