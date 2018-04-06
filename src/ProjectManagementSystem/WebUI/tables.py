import django_tables2 as tables
from WebAPI.choices import *
from django_tables2.utils import A
from WebAPI.models import *
import pdb
class TicketTable(tables.Table):

    amend = tables.TemplateColumn('<input type="checkbox"/>', verbose_name="")
    name = tables.LinkColumn('ticket_detail',  args=[A('name')], accessor='name')
    priority = tables.LinkColumn('new_project',accessor='priority')
    in_progress = tables.Column(accessor='state', verbose_name ="State")
