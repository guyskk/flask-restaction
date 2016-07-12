import pkg_resources
from .exporters import exporters, exporter
from .api import Api

__flask_restaction__ = pkg_resources.get_distribution("flask_restaction")
__version__ = __flask_restaction__.version
__all__ = ["Api", "exporters", "exporter"]
