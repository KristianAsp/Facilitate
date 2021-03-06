import pdb, re, uuid, requests, json, hashlib
from datetime import datetime, timedelta
from pytz import timezone
from django.db.models import Q
from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse, JsonResponse, QueryDict, HttpResponseRedirect, HttpResponseBadRequest, Http404
from django.core.serializers.json import DjangoJSONEncoder
from django.template.loader import render_to_string, get_template
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from django.core import serializers
from django.core.mail import EmailMessage
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django_tables2 import RequestConfig
from .tables import TicketTable
from .forms import *
from WebAPI.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .decorators import *
from .constant_strings import *
from notify.signals import notify

API_URL = 'http://127.0.0.1:8000/api/'

######
# Obtain authentication token from API. Stored in the request.session and used to access the API in future requests.
######
def get_auth_token(request, username, password):
    URL = API_URL + 'get_auth_token/'
    data = dict(username = username, password = password)
    try:
        r = requests.post(URL, data = data)
        data_json = r.json()
        return data_json['token']
    except:
        return ""

def user_login(request):
    form = LoginForm(request.POST)

    if form.is_valid():
        username = request.POST.get("username") #cleaned_data.get did not work. Find out why
        password = request.POST.get("password") #cleaned_data.get did not work. Find out why

        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            #request.session['auth'] = get_auth_token(request, username = username, password = password)
            return HttpResponseRedirect('/dashboard/')
    return render(request, 'UI/login.html', {'form': form})



######
# Load the Dashboard. If the user is a member of a project, redirect to /project/ProjectID instead.
######
@login_required
def dashboard_index(request):
    data = {'path' : 'dashboard' }
    setDefaultRequestValues(request)

    if ACTIVE_PROJECT_ACCESSOR in request.session:
        return HttpResponseRedirect("/dashboard/" + request.session[ACTIVE_PROJECT_ACCESSOR])

    template = loader.get_template('UI/user/dashboard.html')
    return HttpResponse(template.render(data, request))


@login_required
def profile_index(request):
    form = ProfileForm()
    context = { 'form' : form,
                'user' : request.user,
                }

    ####
    # Used to move error messages from one view to another when using a redirect
    ####
    if 'current_password_error' in request.session:
        context['current_password_error'] = request.session['current_password_error']
        del request.session['current_password_error']
    if 'matching_password_error' in request.session:
        context['matching_password_error'] = request.session['matching_password_error']
        del request.session['matching_password_error']

    return render(request, 'UI/user/profile.html', context)

####
# get projects that the current user belongs to.
####
def getProjects(request):
    return request.user.profile.projects.all()

####
# Get details of an individual project with an ID equal to pk
####
def getSingleProject(request, pk):
    try:
        return Project.objects.get(pk = pk)
    except:
        return None


@login_required
@check_if_valid_project_id
def settings_index(request):
    form = SettingsForm()
    return render(request, 'UI/user/settings.html', {'form': form})

####
# Registers a new user and creates a Profile objects at the same time.
# Uses the Invitation Model to automatically add project if there are invitations for that email address.
####
def user_register(request):
    form = RegisterForm(request.POST)
    context = {}
    if form.is_valid():
        if User.objects.filter(email = form.cleaned_data.get('email')).count() == 0:
            if re.match("^[\w_-]+$", form.cleaned_data.get('username')):
                user = form.save(commit=False)
                user.set_password(form.cleaned_data.get('password'))
                user.save()
                profile = Profile(user = user)
                invitations = Invitation.objects.filter(user = user.email)

                profile.save()
                for invitation in invitations:
                    profile.projects.add(invitation.project)

                profile.save()
                login(request, user)
                #request.session['auth'] = get_auth_token(request, username = user.username, password = form.cleaned_data.get('password'))
                return HttpResponseRedirect('/dashboard/')
            else:
                context['error'] = "Please only use standard characters in your username."
        else:
            context['error'] = "That email address is taken."
    context['form'] = form
    return render(request, 'UI/register.html', context)

def register_index(request):
    if request.method == "POST":
        return user_register(request)

    if request.method == "GET":
        if request.user.is_authenticated:
            return HttpResponseRedirect("/dashboard")
        form = RegisterForm()
        return render(request, 'UI/register.html', {'form': form})

    return HttpResponseBadRequest

def login_index(request):
    if request.method == "POST":
        return user_login(request)

    if request.method == "GET":
        if request.user.is_authenticated:
            return HttpResponseRedirect("/dashboard")
        form = LoginForm()
        return render(request, 'UI/login.html', {'form': form})

    return HttpResponseBadRequest

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')

def index(request):
    context = {}
    template = loader.get_template('UI/index.html')
    return HttpResponse(template.render(context, request))

####
# Ensures that some default values in the request.session dictionary are always set. This is especially important after
# deleting/creating a new project and/or board.
####
def setDefaultRequestValues(request):
    projects = Profile.objects.get(user = request.user).projects.all()
    try:
        if(len(projects) > 0) and ACTIVE_PROJECT_ACCESSOR not in request.session:
            request.session[ACTIVE_PROJECT_ACCESSOR] = str(projects[0].pk)
            request.session['is_owner'] = projects[0].owner == request.user
            request.session['active_board'] = Board.objects.get(project = Project.objects.get(id = request.session[ACTIVE_PROJECT_ACCESSOR]), default = True).id
            return True
    except:
        pass
    return False

####
# Create new project / Get the template to create new project.
####
@login_required
def new_project(request):
    if request.method == "GET":
        form = ProjectForm()
        context = {
                    'form' : form,
                    'projects' : getProjects(request),
                }
        if ACTIVE_PROJECT_ACCESSOR not in request.session:
            setDefaultRequestValues(request)

        return render(request, 'UI/project/new.html', context)

    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.visibility = 'public' in request.POST
            project.save()
            profile = Profile.objects.get(user = request.user)
            profile.projects.add(project)

            request.session[ACTIVE_PROJECT_ACCESSOR] = str(project.pk)
            request.session['active_board'] = Board.objects.get(project = project, default = True).pk

            ####
            # Used to move error and success messages from one view to another when using a redirect
            ####
            messages.success(request, 'Your project was successfully created')
            request.session['is_owner'] = project.owner == request.user

            return redirect('/project/new/')

####
# Delete a project and redirect back to the same page.
####
@login_required
def delete_project(request):
    if request.method == "POST":
        data = { 'Authorization' : 'Token ' + request.session.get('auth', "")}
        try:
            projectID = request.session[ACTIVE_PROJECT_ACCESSOR]
            project = Project.objects.get(pk = projectID)
            project.delete()
            messages.success(request, 'Your project was successfully created')
            del request.session[ACTIVE_PROJECT_ACCESSOR]
            del request.session['active_board']
        except:
            messages.error(request, 'Something went wrong. Please try again.')
        return redirect('/project/new/')

####
# Displays the dashboard with a specific project displayed.
####
@login_required
@check_if_valid_project_id
def dashboard_project_view(request, pk):
    if 'active_board' not in request.session or pk != request.session[ACTIVE_PROJECT_ACCESSOR]:
        request.session[ACTIVE_PROJECT_ACCESSOR] = str(pk)
        request.session['active_board'] = Board.objects.get(project = Project.objects.get(id = request.session[ACTIVE_PROJECT_ACCESSOR]), default = True).id
    project = getSingleProject(request, pk);

    try:
        request.session['is_owner'] = project.owner.id == request.user.id
    except KeyError:
        request.session['is_owner'] = False

    data = {
            'projects' : getProjects(request),
            'tickets' : getTickets(request),
            'states' : getBoardStates(request),
            'boards' : getBoards(request),
            'missing_states' : getMissingDefaultStates(request),
            'current_board_name' : Board.objects.get(pk = request.session['active_board']).title,
            'path' : 'dashboard',
            }
    template = loader.get_template('UI/user/dashboard.html')
    return HttpResponse(template.render(data, request))

####
# Use request.session[ACTIVE_PROJECT_ACCESSOR] to obtain all tickets belonging to said project
####
def getTickets(request):
    try:
        tickets = Ticket.objects.filter(project = Project.objects.get(id = request.session[ACTIVE_PROJECT_ACCESSOR])).order_by('priority')
        return tickets
    except ValueError:
        return None

####
# Use request.session[ACTIVE_PROJECT_ACCESSOR] to obtain all states belonging to the default board project
####
def getDefaultStates(request):
    if ACTIVE_PROJECT_ACCESSOR in request.session:
        board_object = Board.objects.get(project = Project.objects.get(pk = request.session[ACTIVE_PROJECT_ACCESSOR]), default = True)
        states = State.objects.filter(board = board_object).order_by('order')
        return states
    return None

####
# Use request.session['active_board'] to obtain all states belonging to specific project
####
def getBoardStates(request):
    if ACTIVE_PROJECT_ACCESSOR in request.session:
        board_object = Board.objects.get(pk = request.session['active_board'])
        states = State.objects.filter(board = board_object).order_by('order')
        return states
    return None
####
# Use request.session[ACTIVE_PROJECT_ACCESSOR] to obtain all boards belonging to said project
####
def getBoards(request):
    if ACTIVE_PROJECT_ACCESSOR in request.session:
        project = Project.objects.get(id = request.session[ACTIVE_PROJECT_ACCESSOR])
        boards = Board.objects.filter(project = project)
        return boards
    return None


####
# Obtain the states missing from the board.
####
def getMissingDefaultStates(request):
        if ACTIVE_PROJECT_ACCESSOR in request.session and 'active_board' in request.session:
            board = Board.objects.get(pk = request.session['active_board'])
            board_states = State.objects.filter(board = board).values_list('name', flat=True)
            current_project = Project.objects.get(pk = request.session[ACTIVE_PROJECT_ACCESSOR])

            default_board = Board.objects.get(project = current_project, default = True)
            missing_default_states = State.objects.filter(board = default_board).exclude(name__in=board_states)
            return missing_default_states
        return None

####
# Display all tickets in a TicketTable
####
@login_required
@check_if_valid_project_id
def dashboard_ticket_view(request):
    tickets = getTickets(request)

    table = TicketTable(tickets, request = request)
    data = {
        'projects' : getProjects(request),
        'tickets' : getTickets(request),
        'type_choices' : TYPE_CHOICES,
        'priority_choices' : PRIORITY_CHOICES,
        'state_choices' : STATE_CHOICES,
        'table' : table,
        'users' : getUsersForProject(request, request.session[ACTIVE_PROJECT_ACCESSOR]),
        'path' : 'tasks',
        }
    return render(request, 'UI/project/tasklist.html', data)

@login_required
def new_ticket_view(request):
    if request.method == "GET":
        form = NewTicketForm()
        context = { 'form' : form }
        return render(request, 'UI/project/tickets/new.html', context )
    elif request.method == "POST":
        form = NewTicketForm(request.POST)
        if form.is_valid():
            context = { 'form' : form,
                        }
            post_fields = form.cleaned_data
            post_fields['project'] = request.session[ACTIVE_PROJECT_ACCESSOR]
            try:
                post_fields['assigned_to'] = User.objects.get(username = post_fields['assigned_to'])
            except User.DoesNotExist:
                post_fields['assigned_to'] = None
            try:
                t = Ticket(name = post_fields['name'], created_by = request.user, description = post_fields['description'], project = Project.objects.get(pk = post_fields['project']), type = post_fields['type'], priority = post_fields['priority'], assigned_to = post_fields['assigned_to'])
                t.save()
                messages.success(request,  'The ticket was successfully created')
            except User.DoesNotExist:
                pass
            except:
                messages.error(request, 'Something went wrong. Please try again.')

            return render(request, 'UI/project/tickets/new.html', context)

def getUsersForProject(request, project_id):
    profiles = Profile.objects.filter(projects__in=[project_id])
    users = User.objects.filter(profile__in=profiles)
    return users

@login_required
def project_settings_view(request):
    if request.method == "GET":
        data = getUsersForProject(request, request.session[ACTIVE_PROJECT_ACCESSOR])
        context = {
                    'path' : 'settings',
                    'project' : Project.objects.get(pk = request.session[ACTIVE_PROJECT_ACCESSOR]),
                    'projects' : getProjects(request),
                }
        context['data'] = data
        return render(request, 'UI/project/settings.html', context)
    elif request.method == "POST":
        return user_project_settings(request)

@login_required
def user_project_settings(request):
    if request.method == "POST":
        error_message = None
        try:
            user = User.objects.get(Q(username = request.POST.get('txtUser')) | Q(email = request.POST.get('txtUser')) )
            project = Project.objects.get(pk = request.session[ACTIVE_PROJECT_ACCESSOR])
            if project not in user.profile.projects.all():
                user.profile.projects.add(project)
                user.profile.save()
                #Stores in request.session temporarily to bypass redirect
                messages.success(request, request.POST['txtUser'] + ' was successfully added to the project.')
            else:
                error_message = "This user is already a collaborator on this project!"
                messages.error(request, error_message)
        except (User.DoesNotExist, Profile.DoesNotExist):
            EMAIL_REGEX = "[^@]+@[^@]+\.[^@]+" #REGEX Matching all emails
            if re.match(EMAIL_REGEX, request.POST['txtUser']): ##If the non-existant user is an email address, send an invitation by email to use the software.
                createInvitation(request.user, request.POST['txtUser'], request.session[ACTIVE_PROJECT_ACCESSOR])
                message = "An invitation has been sent to this email address."

                messages.success(request, message)
            else:
                error_message = "No user with that name."
                messages.error(request, error_message)
        except PermissionDenied:
            error_message = "You are not allowed to do that."
            messages.error(request, error_message)
        return redirect('/project/collaborators')
    elif request.method == "GET":
        data_arr = []
        if ACTIVE_PROJECT_ACCESSOR in request.session:
            #Get list of usernames for users belonging to the project.
            data = getUsersForProject(request, request.session[ACTIVE_PROJECT_ACCESSOR])
            for user in data:
                data_arr.append(user.username)
        return JsonResponse(data_arr, safe=False)

def createInvitation(user, email, project):
    try:
        invitation = Invitation.objects.get(project = project, user = email)
        print("An invitation for this user already exist")
    except Invitation.DoesNotExist:
        project = Project.objects.get(id = project)
        invitation = Invitation(project = project, user = email, invitor = user)
        invitation.save()
        print("Created an invitation")

def view_user_profile(request, slug):
    responseJsonParsed = None
    form = ProfileForm()
    context = {
                'form' : form
            }

    if request.user.is_authenticated:
        try:
            user = User.objects.filter(username = slug).values()[0]
            context['user'] = user
            context['projects'] = getProjects(request)
        except:
            raise Http404
    else:
        context['user'] = User.objects.filter(username = slug).values()[0]
    return render(request, 'UI/user/profile.html', context)

###
# Searches the projects and user for queryself.
# Uses a paginator to paginate results in case there are too many users to display.
def search(request):
    if 'type' not in request.GET:
        return redirect(request.get_full_path() + "&type=user")

    if request.GET['type'] == "user":
        users = filterUsers(request, request.GET['query'])
        projects = filterProjects(request, request.GET['query'])

        paginator = Paginator(users, 10)
        page = request.GET.get('page', 1)

        try:
            search_result = paginator.page(page)
        except PageNotAnInteger:
            search_result = paginator.page(1)
        except EmptyPage:
            search_result = paginator.page(paginator.num_pages)

        context = {
                'result' : search_result,
                'userscount' : len(users),
                'projectscount' : len(projects),
                }

        if request.user.is_authenticated:
            context['projects'] = getProjects(request)

    elif request.GET['type'] == "project":
        users = filterUsers(request, request.GET['query'])
        projects = filterProjects(request, request.GET['query'])

        paginator = Paginator(projects, 10)
        page = request.GET.get('page', 1)

        try:
            search_result = paginator.page(page)
        except PageNotAnInteger:
            search_result = paginator.page(1)
        except EmptyPage:
            search_result = paginator.page(paginator.num_pages)

        context = {
                'result' : search_result,
                'userscount' : len(users),
                'projectscount' : len(projects),
                }

        if request.user.is_authenticated:
            context['projects'] = getProjects(request)

    return render(request, 'UI/search/search.html', context )

# Belongs to search function, to filter users based on query
def filterUsers(request, query):
    list_of_query_words = query.split(" ")
    q = Q()
    for word in list_of_query_words:
        q |= Q(username__icontains = word)
    filteredUsers = User.objects.filter(q)
    return filteredUsers;

# A part of searching, to filter projects based on query
def filterProjects(request, query):
    list_of_query_words = query.split(" ")
    q = Q()
    for word in list_of_query_words:
        q |= Q(name__icontains = word, visibility = True)
    filteredProjects = Project.objects.filter(q)
    return filteredProjects;

def remove_user_from_project(request, slug):
    user = User.objects.get(username = slug)
    profile = Profile.objects.get(user = user)
    project = Project.objects.get(id = request.session[ACTIVE_PROJECT_ACCESSOR])
    profile.projects.remove(project)
    messages.success(request, user.username + ' was successfully removed from the project.')
    return HttpResponseRedirect('/project/collaborators')

def forgotten_password(request):
    if request.method == "GET":
        return render(request, 'UI/forgotten_password.html')
    elif request.method == "POST":
        email = request.POST['email']
        try:
            user = User.objects.get(email = email)
        except User.DoesNotExist:
            return render(request, 'UI/forgotten_password.html', {'error' : 'We could not find a user with that email address. Please try again'})

        profile = Profile.objects.get(user = user)
        profile.reset_password_hash = uuid.uuid1().hex
        profile.save()
        send_email('UI/email/reset_password.html', ['kristian.aspevik@gmail.com'], 'Reset Password', slug = profile.reset_password_hash, )
        return render(request, 'UI/forgotten_password.html', {'message' : 'An email has been sent to ' + email})

def reset_password(request, slug):
    if request.method == "GET":
        try:
            profile = Profile.objects.get(reset_password_hash = slug)
            user = User.objects.get(profile = profile)
        except (Profile.DoesNotExist, User.DoesNotExist):
            raise Http404
        return render(request, 'UI/reset_password.html', {'slug' : slug})
    elif request.method == "POST":
        try:
            profile = Profile.objects.get(reset_password_hash = slug)
            user = User.objects.get(profile = profile)
        except (Profile.DoesNotExist, User.DoesNotExist):
            raise Http404

        new_pass = request.POST.get('password')
        user.set_password(new_pass)
        user.save()
        profile.reset_password_hash = None
        profile.save()
        return render(request, 'UI/reset_password.html', {'message' : 'Success', 'slug' : slug})

# Generic Helper function to send email to a set of recipients
def send_email(template, recipients, subject, **kwargs):
    message = get_template(template).render(kwargs)
    email = EmailMessage(subject, message, to=recipients)
    email.content_subtype = 'html'
    email.send()

@login_required
def ticket_detail(request, slug):
    context = {}
    if request.method == "GET":
        try:
            ticket = Ticket.objects.get(pk = slug)
            context = {
                        'ticket' : ticket,
                        'type_choices' : TYPE_CHOICES,
                        'priority_choices' : PRIORITY_CHOICES,
                        'states' : getDefaultStates(request),
                        'comments' : Comment.objects.filter(ticket = ticket).order_by('created_on')
                        }
        except Ticket.DoesNotExist:
            raise Http404
        return render(request, 'UI/project/tickets/detail_view.html', context)

    ###
    # If the Ajax PUT request is sent to the view
    ###
    elif request.method == "PUT":
        data_arr = {}
        try:
            send_alert = False
            ticket = Ticket.objects.get(pk = int(slug))
            put = QueryDict(request.body)
            if 'name' in put:
                ticket.name = put.get('name')
            if 'assigned_to' in put:
                try:
                    user = User.objects.get(username = put.get('assigned_to'))
                    ticket.assigned_to = user
                    if not ticket.associated_users.filter(username = put.get('assigned_to')).exists():
                        ticket.associated_users.add(user)
                except User.DoesNotExist:
                    ticket.assigned_to = None
            if 'comment' in put:
                comment = Comment(user = request.user, content = put.get('comment'), ticket = ticket)
                comment.save()
            if 'state' in put:
                if put.get('state') != ticket.state:
                    send_alert = True

                ticket.state = put.get('state')
            ticket.save()
            data_arr['ticket'] = "SUCCESS"
            if send_alert:
                send_notification(request = request, target = ticket, recipient_list=list(ticket.associated_users.all().exclude(username = request.user.username)), actor=request.user, verb='updated the state of ', nf_type='updated_state')

        except Ticket.DoesNotExist:
            raise Http404
        except:
            pass
        return JsonResponse(data_arr)

    elif request.method == "POST":
        ticket = Ticket.objects.get(pk = int(slug))
        ticket.name = request.POST.get('ticket_name')
        ticket.state = State.objects.get(board = Board.objects.get(project = Project.objects.get(pk = request.session[ACTIVE_PROJECT_ACCESSOR]), default = True), name = request.POST.get('ticket_state')).short_name
        ticket.description = request.POST.get('description')
        for i in range(0, len(PRIORITY_CHOICES)):
            if PRIORITY_CHOICES[i][1] == request.POST.get('ticket_priority'):
                ticket.priority = PRIORITY_CHOICES[i][0]
                break

        for i in range(0, len(TYPE_CHOICES)):
            if TYPE_CHOICES[i][1] == request.POST.get('ticket_type'):
                ticket.type = TYPE_CHOICES[i][0]
                break

        if(request.POST.get('ticket_assigned_to') != 'Unassigned'):
            if request.POST.get('ticket_assigned_to') == '':
                ticket.assigned_to = None
                ticket.save()
            else:
                try:
                    profile = Profile.objects.get(user = User.objects.get(username = request.POST.get('ticket_assigned_to')))
                    if not profile.projects.get(pk = request.session[ACTIVE_PROJECT_ACCESSOR]):
                        raise Profile.DoesNotExist
                    else:
                        ticket.assigned_to = profile.user
                        ticket.save()
                except (Profile.DoesNotExist, Project.DoesNotExist):
                    messages.error(request, "There is no user with that username working on this project. Please try with a different username.")
        else:
            ticket.save()
        return redirect('/project/tickets/detail/' + slug + '/')

@login_required
def delete_ticket(request, id):
    if request.method == "POST":
        try:
            ticket = Ticket.objects.get(pk = int(id))
            ticket.delete()
            messages.success(request, 'The ticket was successfully deleted')
        except:
            pass
    return redirect('/dashboard/tasks/new')

@login_required
def delete_state(request, pk):
    if request.method == "POST":
        board = Board.objects.get(pk = request.session['active_board'])
        state = State.objects.get(pk = pk)
        slug = state.short_name
        state.delete()
        if(board.default == True):
            boards = Board.objects.filter(project = board.project)
            states = State.objects.filter(board__in = boards, short_name = slug)
            states.delete()
        request.session['next'] = '#States'
        return redirect("/project/boards")
    return redirect("/project/boards")

@login_required
def new_board(request):
    board = Board(owner = request.user, default = False, project = Project.objects.get(id = request.session[ACTIVE_PROJECT_ACCESSOR]), title="Copy of Default Board")
    board.save()
    request.session['active_board'] = board.id
    return redirect("/dashboard/")

@login_required
def delete_board(request):
    board = Board.objects.get(pk = request.session['active_board'])
    if not board.default == True:
        board.delete()
        request.session['active_board'] = Board.objects.get(project = Project.objects.get(id = request.session[ACTIVE_PROJECT_ACCESSOR]), default = True).pk
    return HttpResponseRedirect("/dashboard/")

@login_required
def update_board_display(request, pk):
    request.session['active_board'] = pk
    nextURL = request.GET.get('next', '/')

    return HttpResponseRedirect(nextURL)

@login_required
def project_ticket_changes(request):
    project = Project.objects.get(pk = request.session[ACTIVE_PROJECT_ACCESSOR])
    tickets = Ticket.objects.filter(project = project, last_modified__gt = datetime.now() - timedelta(seconds=2))

    ticketsList = []
    for ticket in tickets:
        ticketsList += [{
        'id' : ticket.pk,
        'last_modified' : ticket.last_modified.astimezone(timezone('Europe/London')),
        'name': ticket.name,
        'assigned_to' : ticket.assigned_to.first_name if ticket.assigned_to is not None else "",
        'priority': ticket.priority,
        'state': ticket.state,
        }]

    data_arr = { 'data' : ticketsList }
    return JsonResponse(data_arr)

@login_required
def updateUserDetails(request):
    if request.method == "POST":
        try:
            user = request.user
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.username = request.POST.get('username')
            user.email = request.POST.get('email')
            user.save()

            messages.success(request, "Your profile was successfully updated")
        except User.DoesNotExist:
            messages.error(request, "Something went wrong")
            raise Http404
        return redirect('/' + request.user.username)

@login_required
def updateUserPassword(request):
    if request.method == "POST":
        try:
            user = request.user
            if not user.check_password(request.POST.get('current_password')):
                request.session['current_password_error'] = 'Your current password is incorrect'
            elif request.POST.get('password') != request.POST.get('confirm_password'):
                request.session['matching_password_error'] = "The passwords do not match"
            else:
                user.set_password(request.POST.get('password'))
                user.save()
                user = authenticate(request, username = user.username, password = request.POST.get('password'))
                if user is not None:
                    login(request, user)
                    messages.success(request, "Your password was successfully updated")
                    #request.session['auth'] = get_auth_token(request, username = user.username, password = request.POST.get('password'))
        except User.DoesNotExist:
            messages.error(request, "Something went wrong")
            raise Http404

        return redirect('/' + request.user.username)

#Display the calendar or create a new event.
@login_required
def displayCalendar(request):
    events = Event.objects.filter(project = Project.objects.get(pk = request.session[ACTIVE_PROJECT_ACCESSOR]))
    if request.method == "GET":
        form = NewEventForm()
        context = {
                    'form' : form,
                    'projects' : Profile.objects.get(user = request.user).projects.all(),
                    'events' : events,
                    'path' : 'calendar',
                }
        return render(request, 'UI/project/calendar/calendar.html', context)

    elif request.method == "POST":
        request.POST = request.POST.copy()

        request.POST['project'] = request.session[ACTIVE_PROJECT_ACCESSOR]
        request.POST['added_by'] = request.user.pk
        request.POST['start_date'] = datetime.strptime(request.POST['start_date'], "%d/%m/%Y").date()
        request.POST['end_date'] = datetime.strptime(request.POST['end_date'], "%d/%m/%Y").date()


        form = NewEventForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'UI/project/calendar/calendar.html', { 'events' : events, 'form' : NewEventForm(), 'message' : 'The event was successfully created.'})
        return render(request, 'UI/project/calendar/calendar.html', { 'events' : events, 'form' : form, 'warning' : 'Something went wrong when creating the event. Try again.' })

@login_required
def displayBoardSettings(request):
    active_board = Board.objects.get(pk = request.session['active_board'])
    if request.method == "GET":
        context = {
                    'boards' : getBoards(request),
                    'active_board' : active_board,
                    'states' : State.objects.filter(board = active_board).order_by('order'),
                    'missing_states' : getMissingDefaultStates(request),
                    'form' : NewStateForm(),
                    'next' : request.session.get('next', ''),
                    'path' : 'boards',
                    'projects' : Profile.objects.get(user = request.user).projects.all(),
                }

        # Transfer temp values from request.session to context
        if 'next' in request.session:
            del request.session['next']
        return render(request, 'UI/project/boards/settings.html', context)
    elif request.method == "POST":
        active_board.title = request.POST.get('board_title')
        username = request.POST.get('board_owner')
        if username != active_board.owner.username:
            if username == '':
                messages.error(request, 'Oops. A board must have an owner')
            else:
                try:
                    user = User.objects.get(username = username)
                    active_board.owner = user
                    active_board.save()
                    messages.success(request, 'The board has been updated.')
                except User.DoesNotExist:
                    messages.error(request, 'We couldn\'t find a user with that username working on this project. Try again!')
        else:
            active_board.save()
            messages.success(request, 'The board was saved')
        return redirect('/project/boards')

@login_required
def updateStateOrder(request):
    context = {}
    try:
        active_board = Board.objects.get(pk = request.session['active_board'])
        stateIDs = request.POST.get('data').split(", ")
        states = State.objects.filter(id__in = stateIDs)
        for state in states:
            state.order = stateIDs.index(str(state.pk)) + 1
            state.save()
    except:
        messages.error(request, "Something went wrong when trying to update the order. Please refresh and try again.")
    return JsonResponse(context)

@login_required
def newState(request):
    if request.method == "POST":
        context = {}
        try:
            state = State(name = request.POST.get('name'), short_name = request.POST.get('short_name'), board = Board.objects.get(pk = request.session['active_board']), order = 100)
            state.save()
            context['state_id'] = state.pk
            context['name'] = state.name
            context['short_name'] = state.short_name
        except:
            messages.error(request, "Something went wrong when trying to create the new state. Please refresh and try again.")
        return JsonResponse(context, safe = False)

    elif request.method == "GET":
        return redirect('/project/boards')

@login_required
def copyStateToSubBoard(request, pk):
    if request.method == "POST":
        context = {}
        try:
            originalState = State.objects.get(pk = pk)
            state = State(name = originalState.name, short_name = originalState.short_name, board = Board.objects.get(pk = request.session['active_board']), order = 100)
            state.save()
            context['state_id'] = state.pk
            context['name'] = state.name
            context['short_name'] = state.short_name
        except:
            messages.error(request, "Something went wrong when trying to create the new state. Please refresh and try again.")
        return JsonResponse(context, safe = False)

    elif request.method == "GET":
        return redirect('/project/boards')

@login_required
def viewCollaborators(request):
    data = getUsersForProject(request, request.session[ACTIVE_PROJECT_ACCESSOR])
    context = {
                'path' : 'collaborators',
                'data' : data,
                'projects' : Profile.objects.get(user = request.user).projects.all(),
    }

    return render(request, 'UI/project/collaborators.html', context)

@login_required
def update_project(request):
    if request.method == "POST":
        project = Project.objects.get(pk = request.session[ACTIVE_PROJECT_ACCESSOR])
        if 'name' in request.POST:
            new_name = request.POST.get('name')
            if new_name != "":
                project.name = new_name
                project.save()
                messages.success(request, "The project has been renamed to " + new_name)

            else:
                message.error(request, "A project cannot have a blank name")
        else:
            if request.POST.get('visibility') == "public":
                project.visibility = True

            else:
                project.visibility = False
            project.save()
            messages.success(request, "The project visibility has been saved.")

        return redirect('/project/settings')

@login_required
def add_comment(request, pk):
    ticket = Ticket.objects.get(pk = pk)
    comment = Comment(user = request.user, content = request.POST.get('comment'), ticket = ticket)
    comment.save()

    send_notification(request = request, target = ticket, recipient_list=list(ticket.associated_users.all().exclude(username = request.user.username)), actor=request.user, verb='added a comment to ', nf_type='followed_user')
    return redirect('/project/tickets/detail/' + pk)

def send_notification(request, recipient_list, actor, verb, nf_type, target):
    if len(recipient_list) > 0:
        notify.send(request.user, recipient_list=recipient_list, actor=actor, verb=verb, nf_type = nf_type, target = target)
