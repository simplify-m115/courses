# -*- coding: utf-8 -*-

import json
import logging

from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


def send_welcome_mail(students, teacher, course):
    for student in students:
        welcome_mail = request.env['courses.send_mail'].create({
            'course': course.id,
            'student': student.id,
            'teacher': teacher.id
        })
        welcome_mail.sudo().send_welcome_mail()


class CoursesStudents(CustomerPortal):

    @http.route("/course/<int:courses_id>/", type='http', auth='user', website=True)
    def students_in_courses(self, courses_id):
        course = http.request.env['courses.courses'].sudo().search([
            ('id', '=', courses_id)
        ], limit=1)
        if course:
            partner = request.env.user.partner_id
            teacher = http.request.env['courses.teachers'].sudo().search([
                ('teacher_access', '=', partner.id)
            ])

            welcomed_students = json.loads(course.welcomed_students)['students']

            not_welcomed_students = course.students_in_course.filtered(lambda l: l.id not in welcomed_students)
            welcomed_students = course.students_in_course.filtered(lambda l: l.id in welcomed_students)
            is_teacher = True if teacher else False
            values = {
                'course': course,
                'not_welcomed_students': not_welcomed_students,
                'welcomed_students': welcomed_students,
                'is_teacher': is_teacher
            }
            return request.render('courses.list_students_in_course', values)
        else:
            return request.render('website.page_404')

    @http.route("/course/<int:courses_id>/welcome_students", type='http', auth='user', website=True, csrf=False)
    def welcome_students_in_course(self, courses_id, **kwargs):
        if request.httprequest.method == 'POST':
            course = http.request.env['courses.courses'].sudo().search([
                ('id', '=', courses_id)
            ], limit=1)
            students_in_course = course.students_in_course
            welcomed_students = json.loads(course.welcomed_students)
            welcome_this_students = list(kwargs.values())
            welcome_this_students = [int(x) for x in welcome_this_students]
            students_in_course = students_in_course.filtered(lambda l: l.id in welcome_this_students)
            welcomed_students['students'] = welcomed_students['students'] + students_in_course.ids
            welcomed_students['students'] = list(dict.fromkeys(welcomed_students['students']))
            welcomed_students = json.dumps(welcomed_students)
            send_welcome_mail(students=students_in_course, teacher=course.course_teacher_name, course=course)
            course.write({'welcomed_students': welcomed_students})
            return http.local_redirect(f'/course/{course.id}/')
