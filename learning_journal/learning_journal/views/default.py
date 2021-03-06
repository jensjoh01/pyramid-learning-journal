"""Configure how the views are handled."""

from pyramid.view import view_config
from datetime import datetime
from pyramid.httpexceptions import HTTPNotFound, HTTPBadRequest, HTTPFound
from pyramid.security import remember, forget
from learning_journal.models import Journal
from learning_journal.security import is_authenticated


@view_config(route_name='home',
             renderer="learning_journal:templates/index.jinja2")
def list_entry(request):
    """Render a list of all entries to home page."""
    entries = request.dbsession.query(Journal).all()
    entries = sorted([entry.to_dict() for entry in entries], key=lambda x: x['id'], reverse=True)
    return {
        "journals": entries
    }


@view_config(route_name='detail_view',
             renderer="learning_journal:templates/details.jinja2")
def detail_view(request):
    """Render a detailed view of the entry clicked on."""
    journal_id = int(request.matchdict['id'])
    entry = request.dbsession.query(Journal).get(journal_id)
    return {
        'entry': entry.to_dict()
    }
    raise HTTPNotFound


@view_config(route_name='new_entry',
             renderer="learning_journal:templates/create.jinja2",
             permission='secret',
             require_csrf=True)
def new_entry(request):
    """Can add a new entry and it adds it the database."""
    if request.method == 'GET':
        return {}

    if request.method == 'POST':
        if not all([field in request.POST for field in ['title', 'content']]):
            return HTTPBadRequest
        now = datetime.now()
        new_entry = Journal(
            title=request.POST['title'],
            date=now.strftime("%B %d, %Y"),
            body=request.POST['content']
        )
        request.dbsession.add(new_entry)
        return HTTPFound(request.route_url('home'))


@view_config(route_name='update',
             renderer="learning_journal:templates/edit.jinja2",
             permission='secret',
             require_csrf=True)
def update(request):
    """Update journal entry and persist the data."""
    journal_id = int(request.matchdict['id'])
    entry = request.dbsession.query(Journal).get(journal_id)
    if not entry:
        raise HTTPFound

    if request.method == 'GET':
        return {
            'entry': entry.to_dict()
        }
    now = datetime.now()
    if request.method == 'POST':
        entry.title = request.POST['title']
        entry.date = now.strftime("%B %d, %Y")
        entry.body = request.POST['content']
        request.dbsession.add(entry)
        request.dbsession.flush()
        return HTTPFound(request.route_url('detail_view', id=entry.id))


@view_config(route_name='login',
             renderer='learning_journal:templates/login.jinja2',
             require_csrf=False)
def login(request):
    """Take in the request from login page. If the method is POST then call
        is_authenticated function to verify username and password. If that
        returns True then the user is logged in, else just stay on the page."""
    if request.method == "GET":
        return {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        if is_authenticated(username, password):
            headers = remember(request, username)
            return HTTPFound(request.route_url('home'), headers=headers)
        else:
            return {}


@view_config(route_name='logout')
def logout(request):
    """."""
    headers = forget(request)
    return HTTPFound(request.route_url('home'), headers=headers)
