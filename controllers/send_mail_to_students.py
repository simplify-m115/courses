from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class SendMailToStudents(CustomerPortal):

    @http.route("/course/send_mail/", type='http', auth='user', website=True)
    def send_mail(self):
        print("mail sent")
