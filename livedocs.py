#!/usr/bin/env python
from livereload import Server, shell


server = Server()

server.watch('docs/source/*.rst', shell('make html', cwd='docs'))
server.serve(root='docs/build/html/')
