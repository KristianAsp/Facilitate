import django_tables2 as tables
from WebAPI.choices import *
import pdb

class TicketTable(tables.Table):
    amend = tables.TemplateColumn('<input type="checkbox"/>', verbose_name="Amend")
    name = tables.LinkColumn('new_project', accessor='name')
    priority = tables.LinkColumn('new_project',accessor='priority')
    in_progress = tables.Column(accessor='state', verbose_name ="State")

    def label_to_value(self, choices, label):
        for (v, k) in choices:
            if v == label:
                return k

    def render_in_progress(self, value):
        state = self.label_to_value(STATE_CHOICES, value)
        return state
