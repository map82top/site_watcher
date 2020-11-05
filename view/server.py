import pykka
from .rest import socketio, app
from site_storage.encoders import AlchemyEncoder
from site_storage.sсhema import SiteConfig
from site_storage.messages import SiteDeleteResponse
from multiprocessing import Process
import json
import threading
import os


class HttpServer(threading.Thread):
    def __init__(self, socketio, app):
        super().__init__()
        self.app = app
        self.socketio = socketio

    def run(self):
        self.socketio.run(self.app)

    def stop(self):
        self.socketio.stop()

class ServerActor(pykka.ThreadingActor):
    def __init__(self, socketio, app):
        super().__init__()
        self.app = app
        self.socketio = socketio
        self.http_server = HttpServer(socketio, app)

    def on_start(self):
        self.http_server.start()

    def on_stop(self):
        self.http_server.stop()

    def on_receive(self, message):
        if isinstance(message, SiteConfig):
            self.on_site_record(message)

        if isinstance(message, SiteDeleteResponse):
            self.on_delete_site(message)

    def on_site_record(self, site):
        socketio.emit('site', json.dumps(site, cls=AlchemyEncoder))

    def on_delete_site(self, response):
        socketio.emit('delete_response', json.dumps(response.__dict__))
