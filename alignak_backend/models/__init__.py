import pkgutil
from importlib import import_module
import logging

log = logging.getLogger(__name__)


def register_models():
    DOMAIN = {}
    files = pkgutil.walk_packages(path=__path__, prefix=__name__ + '.')
    for importer, modname, ispkg in files:
        import_module(modname)

        DOMAIN[modname] = modname.schema
    return DOMAIN
