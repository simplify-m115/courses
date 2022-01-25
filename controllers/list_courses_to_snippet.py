import json
import logging

from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class CoursesStudents(CustomerPortal):
    @http.route("/courses/snippet_data", type='http', auth='user', website=True, csrf=False)
    #TODO CHANGE ROUTE, MAKE SURE THAT DATA GETS TO THE SNIPPET
    def list_courses_to_snippet(self, courses_id, **kwargs):
        if request.httprequest.method == 'GET':
            print("proba")
            courses = request.env['courses.courses'].sudo().search([])
            values = {
                'courses': courses
            }
            return request.render('theme_custom.custom_snippets', values)