from . import _action
from . import _setup


def setup(name, application):
    return _setup.setup(name, application, _action.index, _action.endpoint)
