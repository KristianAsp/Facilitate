from locust import HttpLocust, TaskSet, task

from locust.stats import RequestStats

def noop(*arg, **kwargs):
    print("Stats reset prevented by monkey patch!")

RequestStats.reset_all = noop

import pdb

class UserBehavior(TaskSet):

    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        self.register()

    def on_stop(self):
        self.logout()

    def register(self):
        response = self.client.get("/register/")
        csrf_token = response.cookies['csrftoken']
        self.client.post('/register/', {"username":"kristian", "password":"bvif1234",  "confirm_password" : "bvif1234",'email' : 'kristian.aspevik@gmail.com', 'csrfmiddlewaretoken' : csrf_token})
        self.login()

    @task(1)
    def index(self):
        self.client.get("/")

    def login(self):
        response = self.client.get("/login/")
        csrf_token = response.cookies['csrftoken']
        self.client.post("/login/", {"username":"kristian", "password":"bvif1234", 'csrfmiddlewaretoken' : csrf_token})

    @task(3)
    def dashboard(self):
        self.client.get("/dashboard/")

    @task(4)
    def new_project(self):
        response = self.client.get("/project/new/")
        csrf_token = response.cookies['csrftoken']
        self.client.post("/project/new/", {"name":"Final Year Project", "description":"My Final Year Project view", 'public' : 'on', 'csrfmiddlewaretoken' : csrf_token})

    def new_event(self):
        response = self.client.get("/project/calendar")
        csrf_token = response.cookies['csrftoken']
        self.client.post("/project/calendar", {"event_title":"Final Year Project Deadline", "type":"Project Deadline", 'start_date' : '23/04/2018', 'end_date' : '23/04/2018', 'description' : 'Final project deadline and submission', 'csrfmiddlewaretoken' : csrf_token})

    def logout(self):
        self.client.get("/logout/")

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000
