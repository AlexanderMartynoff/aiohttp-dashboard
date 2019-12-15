from . import _setup
from . import _route
from . import _database


def setup(prefix, application):
    prefix = _setup.normalize_prefix(prefix)
    routes, static_routes = _route.build_routes(prefix)

    return _setup.setup(
        prefix,
        application,
        routes,
        static_routes,
        _route.resource_paths,
        _setup.TinyDBState(),
    )
