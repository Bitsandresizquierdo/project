import re
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from .utils import generate_uid


class Area(models.Model):
    _name = 'nibbana.area'
    _order = 'name'
    _description = 'Area'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    description = fields.Text()
    project_count = fields.Integer(compute='_get_project_count',
                                   string=_('Projects'))
    task_count = fields.Integer(compute='_get_task_count',
                                   string=_('Tasks'))
    reference_count = fields.Integer(compute='_get_reference_count',
                                     string=_('References'))
    active_project_limit = fields.Integer(default=3)
    color = fields.Char(size=7, default='#FFFFFF')
    # Added as easiest way to add bg color to area list without much changes.
    area_color = fields.Char(compute='_get_color')
    uid = fields.Char(required=True, index=True, size=32,
                      default=generate_uid)


    _sql_constraints = [
        ('uid_uniq', 'UNIQUE(uid)', _('The uid must be unique !')),
    ]

    def _get_color(self):
        for rec in self:
            rec.area_color = rec.color

    def _get_project_count(self):
        for rec in self:
            rec.project_count = self.env['nibbana.project'].search_count([
                ('area', '=', rec.id)])

    def _get_task_count(self):
        for rec in self:
            rec.task_count = self.env['nibbana.task'].search_count([
                ('area', '=', rec.id),
                ('state', 'not in', ['Done', 'Cancelled'])])

    def _get_reference_count(self):
        for rec in self:
            rec.reference_count = self.env['nibbana.reference'].search_count([
                ('area', '=', rec.id)])
    
    def toggle_active(self):
        for rec in self:
            rec.active = not rec.active

    @api.constrains('color')
    def _check_color(self):
        if self.color:
            if len(self.color) !=7 or self.color[0] != '#' or \
                    not re.search('[0-9A-Z]{6}', self.color[1:].upper()):
                raise ValidationError(_('Color must be in format of #AABBCC!'))


    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):        
        default = dict(default or {})
        default.update({'uid': generate_uid(self)})
        return super(Area, self).copy(default)
