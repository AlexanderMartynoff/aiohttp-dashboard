from . import action, embedding


def setup(name, application):
    return embedding.setup(name, application, action.index, action.endpoint)