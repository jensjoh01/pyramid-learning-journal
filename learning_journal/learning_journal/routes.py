"""Routes for pages to be served on the web."""


def includeme(config):
    """Include the following routes for static files and uri paths."""
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('detail_view', '/journal/{id:\d+}')
    config.add_route('new_entry', '/journal/new_entry')
    config.add_route('update', '/journal/{id:\d+}/update')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')