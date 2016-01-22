# -*- coding: utf-8 -*-

import sys
import os

sys.path.append(os.path.abspath('_themes'))
sys.path.append(os.path.abspath('.'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'Flask-Restaction'
copyright = u'2015, guyskk'
author = u'guyskk'

# The short X.Y version.
release = __import__('flask_restaction').__version__
# The full version, including alpha/beta/rc tags.
version = release[:release.rindex(".")]
language = 'zh_CN'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# -- Options for HTML output ----------------------------------------------

html_theme = 'flask'
html_theme_path = ['_themes']
html_static_path = ['_static']
html_use_modindex = False
html_show_sphinx = False

# Output file base name for HTML help builder.
htmlhelp_basename = 'Flask-Restactiondoc'

# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'flask-restaction', u'Flask-Restaction Documentation',
     [author], 1)
]

# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'Flask-Restaction', u'Flask-Restaction Documentation',
     author, 'Flask-Restaction', 'One line description of project.',
     'Miscellaneous'),
]

# -- Options for Epub output ----------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'https://docs.python.org/': None}
