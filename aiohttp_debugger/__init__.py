from . import action, embedding


__version__ = '3.0.0a0'


def setup(name, application):
    return embedding.setup(name, application, action.index, action.endpoint)
