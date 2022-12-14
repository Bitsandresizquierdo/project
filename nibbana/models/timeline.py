from datetime import datetime
import logging
from odoo import models, fields, api, _


logger = logging.getLogger(__name__)


EVENT_TYPES = [
    ('created', _('Created')),
    ('updated', _('Updated')),
    ('deleted', _('Deleted')),
]


class Timeline(models.Model):
    _name = 'nibbana.timeline'
    _description = 'Timeline'
    _order = 'create_date desc'

    name = fields.Char(compute=lambda self: self._compute_name())
    active = fields.Boolean(default=True)
    event_type = fields.Selection(selection=EVENT_TYPES,
                                  index=True, required=True)
    task = fields.Many2one('nibbana.task', ondelete='set null')
    task_name = fields.Char(index=True)
    project = fields.Many2one('nibbana.project', ondelete='set null')
    project_name = fields.Char(index=True)
    reference = fields.Many2one('nibbana.reference', ondelete='set null')
    reference_name = fields.Char(index=True)
    note = fields.Text()
    created = fields.Datetime(default=fields.Datetime.now)

    def _compute_name(self):
        for rec in self:
            if rec.project_name:
                rec.name = rec.project_name
            elif rec.task_name:
                rec.name = rec.task_name
            elif rec.reference_name:
                rec.name = rec.reference_name
            else:
                rec.name = _('Undefined')

    @api.model
    def timeline_update_event(self, obj, vals={}, fields=[]):
        # Skip timeline creation if set
        if self.env.context.get('skip_timeline'):
            return
        # Set object id and name
        model_name = obj._name.split('.')[1]
        tm_vals = {'event_type': 'updated'}
        tm_vals['{}'.format(model_name)] = obj.id
        tm_vals['{}_name'.format(model_name)] = obj.name
        # Now create event record for every field change
        for changed_field in [k for k in vals.keys() if k in fields]:
            if changed_field == 'name':
                # Special case with name
                tm_vals['note'] = _('{} "{}" is renamed to "{}"').format(
                                                obj._description,
                                                obj.name,
                                                vals[changed_field])
            elif changed_field == 'state':
                # Special case with name
                tm_vals['note'] = _('{} "{}" state is set to {}').format(
                                                obj._description,
                                                obj.name,
                                                vals[changed_field])
            elif changed_field == 'focus':
                # Special case with name
                tm_vals['note'] = _('{} "{}" focus is {}').format(
                                                obj._description,
                                                obj.name,
                                                'Enabled' if vals[changed_field] == '1' else 'Disabled')
            else:
                tm_vals['note'] = _('{} "{}" {} is changed').format(
                                                obj._description,
                                                obj.name,
                                                changed_field)
            self.env['nibbana.timeline'].create(tm_vals)    



    @api.model
    def timeline_create_event(self, obj):
        # Skip timeline creation if set
        if self.env.context.get('skip_timeline'):
            return        
        # Set object id and name
        model_name = obj._name.split('.')[1]
        tm_vals = {'event_type': 'created'}
        tm_vals['{}'.format(model_name)] = obj.id
        tm_vals['{}_name'.format(model_name)] = obj.name
        tm_vals['note'] = _('{} "{}" is created').format(
                                            obj._description,
                                            obj.name)
        self.env['nibbana.timeline'].create(tm_vals)


    @api.model
    def timeline_unlink_event(self, obj):
        # Skip timeline creation if set
        if self.env.context.get('skip_timeline'):
            return        
        tm_vals = {'event_type': 'deleted'}
        model_name = obj._name.split('.')[1]
        tm_vals['{}_name'.format(model_name)] = obj.name
        tm_vals['note'] = _('{} "{}" deleted').format(
                                            obj._description,
                                            obj.name)
        self.env['nibbana.timeline'].create(tm_vals)
