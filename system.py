import pykka
from site_storage.actor import SiteStorageActor
from site_downloader.actor import SiteDownloaderActor
from view.actor import ServerActor
from view.actor import ServerActor
from analyze.actor import SiteAnalyticActor
from multiprocessing import Process
from view.rest import app, socketio
import os
import sys
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
logging.root.setLevel(level=logging.INFO)

site_storage = SiteStorageActor.start()
os.environ["SITE_STORAGE_URN"] = site_storage.actor_urn

http_server = ServerActor.start(site_storage.proxy())
os.environ["HTTP_SERVER_URN"] = http_server.actor_urn

site_analytic = SiteAnalyticActor.start(site_storage.proxy())
os.environ["SITE_ANALYTIC_URN"] = site_analytic.actor_urn

site_downloader = SiteDownloaderActor.start(site_storage.proxy(), site_analytic.proxy())
os.environ["SITE_DOWNLOADER_URN"] = site_downloader.actor_urn

print("======== SYSTEM STARTED ========")
running = True
while running:
    print('Entre q to exit:')
    enter = input()
    if enter == 'q':
        pykka.ActorRegistry.stop_all()
        running = False

print('Server stopped')