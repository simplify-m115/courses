from odoo import api, fields, models


class Grades(models.Model):
    _name = "courses.grades"
    _description = "Grades"

    course = fields.Many2one(
        'courses.courses',
        string='Course',
        required=False,
        readonly=True
    )

    student = fields.Many2one(
        'courses.students',
        string='Student',
        required=False,
        readonly=True
    )

    grade = fields.Selection([
        ("5","5"),
        ("6","6"),
        ("7","7"),
        ("8","8"),
        ("9","9"),
        ("10","10")],
        string="Grade",
        required=False
    )

