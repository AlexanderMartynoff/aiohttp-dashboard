from . import action, embedding


__version__ = '0.0.1'


def setup(name, application):
    return embedding.setup(name, application, action.index, action.endpoint)