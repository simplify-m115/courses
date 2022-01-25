import logging

from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class Courses(CustomerPortal):

    @http.route("/courses/", type='http', auth='user', website=True)
    def list_courses(self, **kw):
        partner = request.env.user.partner_id
        teacher = http.request.env['courses.teachers'].sudo().search([
            ('teacher_access', '=', partner.id)
        ], limit=1)
        # print(teacher.teacher_courses)
        # print(partner.id)
        if teacher:
            published_courses = list(teacher.teacher_courses.filtered(lambda l: l.course_is_published))
            values = {'courses': published_courses}

            for kurs in published_courses:
                print(kurs.name)
                print(len(kurs.students_in_course))
                print(kurs.number_students_in_course)
        else:
            student = http.request.env['courses.students'].sudo().search([
                ('student_access', '=', partner.id)
            ], limit=1)
            if student:
                # print(student.id)
                all_courses = http.request.env['courses.courses'].sudo().search([])
                student_courses = list()
                for course in all_courses:
                    for students in course.students_in_course:
                        if students.id == student.id:
                            # print(student.id)
                            student_courses.append(course)
                            break
                values = {'courses': student_courses}
            else:
                values = {}

        return request.render('courses.list_courses', values)
