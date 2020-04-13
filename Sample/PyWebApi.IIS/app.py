# -*- coding: utf-8 -*-
"""
This script runs the application using a development server.
"""

import os
import sys
import bottle

# routes contains the HTTP handlers for our server and must be imported.
import routes

if '--debug' in sys.argv[1:] or 'SERVER_DEBUG' in os.environ:
    # Debug mode will enable more verbose output in the console window.
    # It must be set at the beginning of the script.
    bottle.debug(True)

def wsgi_app():
    """Returns the application to make available through wfastcgi. This is used
    when the site is published to Microsoft Azure."""
    return bottle.default_app()

if __name__ == '__main__':
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '6666'))
    except ValueError:
        PORT = 6666

    # Starts a local test server.
    bottle.run(server='wsgiref', host=HOST, port=PORT)
