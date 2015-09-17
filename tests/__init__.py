import imp
import os
fp, pathname, description = imp.find_module("flask_restaction", [os.path.abspath("../")])
imp.load_module("flask_restaction", fp, pathname, description)
