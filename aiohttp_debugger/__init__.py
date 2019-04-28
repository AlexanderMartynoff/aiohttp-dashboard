__version__ = '3.0.0a0'


def setup(name, application):
    from . import action, embedding

    return embedding.setup(
        name,
        application,
        action.routes,
        action.static_routes,
        action.static_path,
    )
