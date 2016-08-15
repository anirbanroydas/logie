from tornado import web
from tornado.web import URLSpec as url
# from sockjs.tornado import SockJSRouter

from settings import settings
from utils import include
# from apps.webapp.views import LogWebsocketHandler


# # Register SocjJsRouter Connection
# SockjsWebsocketRouter = SockJSRouter(LogWebsocketHandler, '/log')

urls = [
    url(r"/static/(.*)", web.StaticFileHandler,
        {"path": settings.get('static_path')}),
]
urls += include(r"/", "apps.webapp.urls")

# urls = urls + SockjsWebsocketRouter.urls
