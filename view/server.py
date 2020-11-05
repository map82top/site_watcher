import pykka
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from site_storage.sсhema import SiteConfig, RegularCheck
from site_storage.encoders import AlchemyEncoder
from site_storage.messages import SiteDeleteResponse
from multiprocessing import Process
import threading
import json
import os



class HttpServer(threading.Thread):
    def __init__(self, socketio, app):
        super().__init__()
        self.app = app
        self.socketio = socketio

    def send_broadcast(self, event_name, message):
        emit('event_name', json.dumps(message.__dict__), broadcast=True, include_self=False)

    def run(self):
        self.socketio.run(self.app)

    def stop(self):
        self.socketio.stop()


class ServerActor(pykka.ThreadingActor):
    def __init__(self, socketio, app):
        super().__init__()
        self.app = app
        self.socketio = socketio
        self.http_process = HttpServer(socketio, app)

    def on_start(self):
        self.http_process.start()
        # self.socketio.run(self.app)

    def on_stop(self):
        self.http_process.stop()
        # self.socketio.stop()

    def on_receive(self, message):
        # if isinstance(message, SiteConfig):
        #     process = Process(target=self.on_site_record, args=[message])
        #     process.start()

        if isinstance(message, SiteDeleteResponse):
            process = Process(target=self.on_delete_site, args=[message])
            process.start()
            # self.on_delete_site(message)

    # def on_site_record(self, site):
        # with self.app.test_request_context():
        #     emit('site', json.dumps(site, cls=AlchemyEncoder), broadcast=True, include_self=False)

    def on_delete_site(self, response):
        # emit('delete_response', json.dumps(response.__dict__))
        with self.app.test_request_context():
            emit('delete_response', json.dumps(response.__dict__), broadcast=True)
