from importlib import resources
__version__ = resources.read_text(__name__, "VERSION").strip()
