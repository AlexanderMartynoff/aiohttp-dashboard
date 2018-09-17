__version__ = '3.0.0a0'


def setup(prefix, application):
    from . import action, embedding

    return embedding.setup(
        prefix,
        application,
        action.routes,
        action.static_routes,
        action.debugger_dir
    )
