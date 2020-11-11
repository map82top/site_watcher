import pykka
from .rest import socketio, app, create_full_site_record, context
from site_storage.encoders import AlchemyEncoder
from site_storage.messages import SiteDeleteResponse, SiteResponse, SubscribeOnSiteUpdates, SubscribeOnVersionsUpdates, SiteVersionResponse
from multiprocessing import Process
import json
import threading
import os
from site_storage.encoders import AlchemyEncoder
from plugins import PluginManager
import logging


logger = logging.getLogger(__name__)

class HttpServer(threading.Thread):
    def __init__(self, socketio, app, context):
        super().__init__()
        self.app = app
        self.socketio = socketio
        self.ctx = context
        self.ctx.push()

    def run(self):
        self.socketio.run(self.app)

    def stop(self):
        with app.test_request_context():
            self.socketio.stop()


class ServerActor(pykka.ThreadingActor):
    def __init__(self, storage_proxy):
        super().__init__()
        self.storage_proxy = storage_proxy
        self.app = app
        self.socketio = socketio
        self.http_server = HttpServer(socketio, app, context)
        self.storage_proxy.subscribe_on_site_update(
            SubscribeOnSiteUpdates(self.actor_ref)
        )
        self.storage_proxy.subscribe_on_site_versions_update(
            SubscribeOnVersionsUpdates(self.actor_ref)
        )

    def on_start(self):
        self.http_server.start()

    def on_stop(self):
        self.http_server.stop()
        print('View stopped')

    def on_receive(self, message):
        try:
            if isinstance(message, SiteResponse):
                self.on_site_record(message)

            if isinstance(message, SiteDeleteResponse):
                self.on_delete_site(message)

            if isinstance(message, SiteVersionResponse):
                self.on_site_version_record(message)
        except Exception as e:
            logger.error('Error occurred {0}'.format(e))

    def on_site_version_record(self, site_version):
        storage_urn = os.environ["SITE_STORAGE_URN"]
        storage_proxy = pykka.ActorRegistry.get_by_urn(storage_urn).proxy()
        site = storage_proxy.get_site_by_id(site_version.site_id).get()

        socketio.emit('site_version', json.dumps(site_version, cls=AlchemyEncoder))
        PluginManager.call_all_plugins({'site': site, 'version': site_version})

    def on_site_record(self, site):
        storage_urn = os.environ["SITE_STORAGE_URN"]
        storage_proxy = pykka.ActorRegistry.get_by_urn(storage_urn).proxy()
        socketio.emit('site', json.dumps(create_full_site_record(storage_proxy, site), cls=AlchemyEncoder))

    def on_delete_site(self, response):
        socketio.emit('delete_response', json.dumps(response, cls=AlchemyEncoder))
