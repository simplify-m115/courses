from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SellCourses(models.Model):
    _name = 'courses.sell_courses'
    _description = "selling courses"
    # _inherit = 'sale.order'

