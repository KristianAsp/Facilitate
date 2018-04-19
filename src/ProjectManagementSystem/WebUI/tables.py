import django_tables2 as tables
from WebAPI.choices import *
from django_tables2.utils import A
from WebAPI.models import *

class TicketTable(tables.Table):
    name = tables.LinkColumn('ticket_detail',  args=[A('pk')], accessor='name', attrs={'td': {'class': 'ticketTableColumn'}})
    type = tables.Column(verbose_name="Type", attrs={
                                                    'td': {
                                                            'class': 'ticketTableColumn',
                                                            'data-Type' : lambda value: value,
                                                            },
                                                    })

    assigned_to = tables.Column(verbose_name="Assignee", default="Unassigned", attrs={
                                                                                'td': {
                                                                                        'class': 'ticketTableColumn',
                                                                                        'data-assignee' : lambda value: value,
                                                                                        },
                                                                                })

    priority = tables.Column(accessor='priority', attrs={
                                                        'td': {
                                                                'class': 'ticketTableColumn',
                                                                'data-Priority' : lambda value: value,
                                                                },
                                                        })

    in_progress = tables.Column(accessor='state', verbose_name ="Status", attrs={
                                                                            'td': {
                                                                                    'class': 'ticketTableColumn',
                                                                                    'data-State' : lambda value: value,
                                                                                    },
                                                                            })

    created_on = tables.Column(accessor='', verbose_name = "Created", attrs={'td': {'class': 'ticketTableColumn'}})
    last_modified = tables.Column(verbose_name = "Last Updated", attrs={'td': {'class': 'ticketTableColumn'}})

    class Meta:
        attrs = {'class' : 'ticketTable table table-hover' }
