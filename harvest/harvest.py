import json
import requests
from requests_oauthlib import OAuth2Session
from urllib.parse import urlparse
from base64 import b64encode
from collections import OrderedDict

HARVEST_STATUS_URL = "http://www.harveststatus.com/api/v2/status.json"


class HarvestError(Exception):
    pass


class HarvestUser:
    def __init__(
            self, uri, email=None, password=None, client_id=None,
            token=None, put_auth_in_header=True):

        self.__uri = uri.rstrip("/")
        parsed = urlparse(uri)
        if not (parsed.scheme and parsed.netloc):
            raise HarvestError("Invalid harvest uri \"{0}\".".format(uri))

        self.__headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0",
        }
        if email and password:
            self.__auth = "Basic"
            self.__email = email.strip()
            self.__password = password
            if put_auth_in_header:
                self.__headers["Authorization"] = "Basic {0}".format(
                    b64encode(
                        "{}:{}".format(email, password).encode("utf-8")
                    ).decode("utf-8")
                )

        elif client_id and token:
            self.__auth = "OAuth2"
            self.__client_id = client_id
            self.__token = token

    @property
    def uri(self):
        return self.__uri

    @property
    def auth(self):
        return self.__auth

    @property
    def email(self):
        return self.__email

    @property
    def password(self):
        return self.__password

    @property
    def client_id(self):
        return self.__client_id

    @property
    def token(self):
        return self.__token

    def status(self):
        return status()

    # Accounts

    def who_am_i(self):
        """User and account information for the current user"""
        return self._get("/account/who_am_i")

    # Client Contacts

    def get_contacts(self, updated_since=None):
        """Get all contacts for an account"""
        url = "/contacts"
        if updated_since is not None:
            url = "{0}?updated_since={1}".format(url, updated_since)
        return self._get(url)

    def get_client_contacts(self, client_id, updated_since=None):
        """Get all contacts for a client"""
        url = "/clients/{0}/contacts".format(client_id)
        if updated_since is not None:
            url = "{0}?updated_since={1}".format(url, updated_since)
        return self._get(url)

    def get_contact(self, contact_id):
        """Get a client contact"""
        return self._get("/contacts/{0}".format(contact_id))

    def create_contact(self, new_contact_id, fname, lname, **kwargs):
        """Create a new client contact"""
        url = "/contacts/{0}".format(new_contact_id)
        kwargs.update({"first-name": fname, "last-name": lname})
        return self._post(url, kwargs)

    def update_contact(self, contact_id, **kwargs):
        """Update a client contact"""
        url = "/contacts/{0}".format(contact_id)
        return self._put(url, kwargs)

    def delete_contact(self, contact_id):
        """Delete a client contact"""
        return self._delete("/contacts/{0}".format(contact_id))

    # Clients

    def get_all_clients(self, updated_since=None):
        """Get all clients"""
        url = "/clients"
        if updated_since is not None:
            url = "{0}?updated_since={1}".format(url, updated_since)
        return self._get(url)

    def get_client(self, client_id):
        """Get a client"""
        return self._get("/clients/{0}".format(client_id))

    def create_client(self, **kwargs):
        """Create a new client"""
        url = "/clients/"
        return self._post(url, kwargs)

    def update_client(self, client_id, **kwargs):
        """"Update Client"""
        url = "/clients/{0}".format(client_id)
        return self._put(url, kwargs)

    def toggle_client_active(self, client_id):
        """(de)activate an existing client"""
        return self._post("/clients/{0}/toggle".format(client_id))

    def delete_client(self, client_id):
        """Delete a client"""
        return self._delete("/clients/{0}".format(client_id))

    # Projects

    def get_all_projects(self, client=None):
        """Show all project"""
        if client:
            return self._get("/projects?client={0}".format(client))
        return self._get("/projects")

    def get_project(self, project_id):
        """Show a project"""
        return self._get("/projects/{0}".format(project_id))

    def create_project(self, **kwargs):
        """Create new project"""
        return self._post("/projects", kwargs)

    def update_project(self, project_id, **kwargs):
        """Update existing project"""
        url = "/projects/{0}".format(project_id)
        return self._put(url, kwargs)

    def toggle_project_active(self, project_id):
        """(de)activate existing project"""
        return self._put("/projects/{0}/toggle".format(project_id))

    def delete_project(self, project_id):
        """Delete a project"""
        return self._delete("/projects/{0}".format(project_id))

    # Task Assignment: Assigning tasks to projects

    def get_all_tasks_from_project(self, project_id):
        """Get all tasks assigned to a given project"""
        return self._get(
            "/projects/{0}/task_assignments".format(project_id))

    def get_task_assigment(self, project_id, task_id):
        """Get one task assignment"""
        return self._get(
            "/projects/{0}/task_assignments/{1}".format(project_id, task_id))

    def assign_task_to_project(self, project_id, **kwargs):
        """Assign a task to a project"""
        return self._post(
            "/projects/{0}/task_assignments/".format(project_id), kwargs)

    def create_task_to_project(self, project_id, **kwargs):
        """Create a new task and assign it to a project"""
        return self._post(
            "/projects/{0}/task_assignments/add_with_create_new_task".format(
                project_id),
            kwargs,
        )

    def remove_task_from_project(self, project_id, task_id):
        """Removing a task from a project"""
        return self._delete(
            "/projects/{0}/task_assignments/{1}".format(project_id, task_id))

    def change_task_from_project(self, project_id, task_id, data, **kwargs):
        """Changing a task for a project"""
        kwargs.update({"task-assignment": data})
        return self._put(
            "/projects/{0}/task_assignments/{1}".format(project_id, task_id),
            kwargs,
        )

    # Tasks

    def get_task(self, task_id):
        """Show one task"""
        return self._get("/tasks/{0}".format(task_id))

    def get_all_tasks(self, updated_since=None):
        """
        Show all tasks. If provided, filter by updated_since.

        updated_since -- UTC date time value (URL encoded)
        """
        if updated_since:
            return self._get("/tasks?updated_since={0}".format(updated_since))
        return self._get("/tasks")

    def create_task(self, **kwargs):
        """Create new task"""
        return self._post("/tasks/", kwargs)

    def delete_task(self, tasks_id):
        """Archive or delete existing task"""
        return self._delete("/tasks/{0}".format(tasks_id))

    def update_task(self, tasks_id, **kwargs):
        """Update an existing task"""
        url = "/tasks/{0}".format(tasks_id)
        return self._put(url, kwargs)

    def activate_task(self, tasks_id):
        """Activate existing archived task"""
        return self._post("/tasks/{0}/activate".format(tasks_id))

    # Expense Categories

    def expense_categories(self):
        """Show all expense categories"""
        return self._get("/expense_categories")

    def create_expense_category(self, new_expense_category_id, **kwargs):
        """Create new expense category"""
        return self._post(
            "/expense_categories/{0}".format(new_expense_category_id),
            kwargs,
        )

    def update_expense_category(self, expense_category_id, **kwargs):
        """Update an existing expense category"""
        return self._put(
            "/expense_categories/{0}".format(expense_category_id), kwargs)

    def get_expense_category(self, expense_category_id):
        """Show expense category"""
        return self._get(
            "/expense_categories/{0}".format(expense_category_id))

    def delete_expense_category(self, expense_category_id):
        """Delete existing expense category"""
        return self._delete(
            "/expense_categories/{0}".format(expense_category_id))

    # Time Tracking

    def get_today(self):
        """
        Retrieves entries for today paired with the projects and tasks that
        can be added to the timesheet by the requesting user
        """
        return self._get("/daily")

    def get_day(self, day_of_the_year, year):
        """
        Retrieves entries for a given day paired with the projects and tasks
        that can be added to the timesheet by the requesting user
        """
        return self._get("/daily/{0}/{1}".format(day_of_the_year, year))

    def get_entry(self, entry_id):
        """Retrieves the selected entry"""
        return self._get("/daily/show/{0}".format(entry_id))

    def toggle_timer(self, entry_id):
        """Starts and stops a timer for a selected entry"""
        return self._get("/daily/timer/{0}".format(entry_id))

    def add_entry(self, data):
        """Create an entry on the daily screen"""
        return self._post("/daily/add", data)

    def delete_entry(self, entry_id):
        """Deletes a day entry"""
        return self._delete("/daily/delete/{0}".format(entry_id))

    def update_entry(self, entry_id, data):
        """
        Updates the note, effort, project or task for a day entry.
        All sensible values are overwritten for the day entry with the
        data provided in your request
        """
        return self._post("/daily/update/{0}".format(entry_id), data)

    # Request methods

    def _get(self, path="/", data=None):
        return self._request("GET", path, data)

    def _post(self, path="/", data=None):
        return self._request("POST", path, data)

    def _put(self, path="/", data=None):
        return self._request("PUT", path, data)

    def _delete(self, path="/", data=None):
        return self._request("DELETE", path, data)

    def _request(self, method="GET", path="/", data=None):
        kwargs = {
            "method": method,
            "url": "{self.uri}{path}".format(self=self, path=path),
            "headers": self.__headers,
            "data": json.dumps(data),
        }
        if self.auth == "Basic":
            requestor = requests
            if "Authorization" not in self.__headers:
                kwargs["auth"] = (self.email, self.password)
        elif self.auth == "OAuth2":
            requestor = OAuth2Session(
                client_id=self.client_id, token=self.token
            )

        try:
            resp = requestor.request(**kwargs)
            if "DELETE" not in method:
                try:
                    return resp.json(object_pairs_hook=OrderedDict)
                except:
                    return resp
            return resp
        except Exception as e:
            raise HarvestError(e)


def status():
    try:
        status = requests.get(HARVEST_STATUS_URL).json().get("status", {})
    except:
        status = {}
    return status
