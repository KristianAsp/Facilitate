from WebAPI.models import *
from .constant_strings import *
from django.shortcuts import render, redirect


######
# Check if the current request.session[ACTIVE_PROJECT_ACCESSOR] is still a va`lid project. Maybe the project has been deleted
# or user has been removed from project
######
def check_if_valid_project_id(fn):
    def wrapped(request, **kwargs):
        if ACTIVE_PROJECT_ACCESSOR in request.session:
            try:
                p = Project.objects.get(id = request.session[ACTIVE_PROJECT_ACCESSOR])
                if p not in request.user.profile.projects.all():
                    raise Project.DoesNotExist
            except Project.DoesNotExist:
                del request.session[ACTIVE_PROJECT_ACCESSOR]
                return redirect('/dashboard')
            except:
                pass
        if 'pk' in kwargs:
            return fn(request, kwargs['pk'])
        else:
            return fn(request)
    return wrapped
