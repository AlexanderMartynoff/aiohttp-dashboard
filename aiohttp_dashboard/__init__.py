from typing import Optional

from . import _setup
from . import _web


def setup(prefix, application, config: Optional[dict] = None):
    prefix = _setup.normalize_prefix(prefix)
    routes, static_routes = _web.build_routes(prefix)

    return _setup.setup(
        prefix,
        application,
        routes,
        static_routes,
        _web.resource_paths,
        config,
    )
