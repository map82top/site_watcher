import pykka
from site_storage.actor import SiteStorageActor
from site_downloader.actor import SiteDownloaderActor
from view.server import ServerActor
from view.server import ServerActor
from multiprocessing import Process
from view.rest import app, socketio
import os

http_server = ServerActor.start(socketio, app)

site_storage = SiteStorageActor.start()
os.environ["SITE_STORAGE_URN"] = site_storage.actor_urn

site_downloader = SiteDownloaderActor.start(site_storage.proxy())
os.environ["SITE_DOWNLOADER_URN"] = site_downloader.actor_urn



print("======== SYSTEM STARTED ========")
while True:
    print('Entre q to exit:')
    enter = input()
    if enter == 'q':
        pykka.ActorRegistry.stop_all()
        exit(0)