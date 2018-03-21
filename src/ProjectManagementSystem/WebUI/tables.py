import django_tables2 as tables
from WebAPI.choices import *
from django_tables2.utils import A
from WebAPI.models import *
import pdb
class TicketTable(tables.Table):
    chs = {}
    amend = tables.TemplateColumn('<input type="checkbox"/>', verbose_name="")
    name = tables.LinkColumn('ticket_detail',  args=[A('name')], accessor='name')
    priority = tables.LinkColumn('new_project',accessor='priority')
    in_progress = tables.Column(accessor='state', verbose_name ="State")

    def label_to_value(self, choices, label):
        for state in chs:
            if state.short_name == label:
                return state.name

    def render_in_progress(self, value):
        state = self.label_to_value(chs, value)
        return state

    def before_render(self, request):
        global chs
        brd = Board.objects.get(id = request.session['active_board'])
        chs = State.objects.filter(board = brd)
