#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals, absolute_import, print_function

DEBUG = True
ALLOW_CORS = True
DATABASE_NAME = 'sqlite'
DATABASE_PATH = 'data/kkblog.db'
ARTICLE_DEST = "data/article_repo"
FORGOT_PASSWORD_AUTH_SECRET = "FORGOT_PASSWORD_AUTH_SECRET"
USER_ADMIN_EMAIL = "admin@admin.com"
USER_ADMIN_PASSWORD = "123456"
USER_ADMIN_REPO_URL = "https://github.com/guyskk/kkblog-article.git"

CACHE_TYPE = "memcached"

# test data
API_PERMISSION_JSON = "API_PERMISSION_JSON"
API_RESOURCE_JSON = "API_RESOURCE_JSON"
API_AUTH_HEADER = "API_AUTH_HEADER"
API_AUTH_SECRET = "API_AUTH_SECRET"
API_AUTH_ALG = "API_AUTH_ALG"
API_AUTH_EXP = "API_AUTH_EXP"
