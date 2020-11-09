import pykka
from site_storage.sсhema import RegularCheck, WatchStatus
from site_storage.messages import UpdateSiteRequest
from site_storage.messages import SiteDeleteResponse, SiteResponse, SubscribeOnSiteUpdates
import os
import urllib.request
from urllib.parse import urldefrag
import time
import threading
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Handler(threading.Thread):
    def __init__(self, downloader):
        super().__init__(daemon=True)
        self.downloader = downloader

    def run(self):
        last_update = datetime.now()
        while True:
            current_time = datetime.now()
            difference = current_time - last_update
            if difference.seconds >= 60:
                self.downloader.recalculate_queue()
                last_update = datetime.now()

            if len(self.downloader.queue) > 0:
                site = self.downloader.queue.pop()
                self.downloader.download_site(site[1])

            time.sleep(5)


class SiteDownloaderActor(pykka.ThreadingActor):
    point_dict = {
        RegularCheck.TWICE_HOUR: 1000,
        RegularCheck.ONCE_HOUR: 500,
        RegularCheck.FOUR_TIMES_DAY: 250,
        RegularCheck.TWICE_DAY: 125,
        RegularCheck.ONCE_DAY: 100
    }

    regular_check_duration = {
        RegularCheck.TWICE_HOUR: 1,
        RegularCheck.ONCE_HOUR: 60,
        RegularCheck.FOUR_TIMES_DAY: 360,
        RegularCheck.TWICE_DAY: 720,
        RegularCheck.ONCE_DAY: 1440
    }

    def __init__(self, storage_proxy, analytic_proxy):
        try:
            super().__init__()
            self.storage_proxy = storage_proxy
            self.analytic_proxy = analytic_proxy
            self.sites = dict()
            self.queue = list()
            self.create_queue()
            self.storage_proxy.subscribe_on_site_update(
                    SubscribeOnSiteUpdates(self.actor_ref)
            )
            self.handle_process = Handler(downloader=self)
        except Exception as e:
            logger.error("Error occurred: {0}".format(e))

    def on_start(self):
        self.handle_process.start()
        # self.handle_process.join()

    def on_stop(self):
        self.handle_process.terminate()

    def create_queue(self):
        for site in self.storage_proxy.get_sites().get():
            self.sites[site.id] = site
            points = self.calculate_priority(site)
            if points > 0:
                self.queue.append((points, site))
        self.queue.sort(key=lambda x: x[0])

    def recalculate_queue(self):
        for site in self.sites.values():
            points = self.calculate_priority(site)
            if points > 0:
                if site.last_watch is not None:
                    self.storage_proxy.update_site(UpdateSiteRequest(id=site.id, status=WatchStatus.NEED_TO_WATCH))

                self.queue.append((points, site))
        self.queue.sort(key=lambda x: x[0])

    def calculate_priority(self, site):
        points = 0

        points = points + self.point_dict[site.regular_check]
        if site.last_watch is None:
            points = points + 10000
        else:
            difference = datetime.now() - datetime.fromisoformat(site.last_watch)
            fine = (difference.seconds // 60) - self.regular_check_duration[site.regular_check]
            if fine < 0:
                points = -1
            else:
                points = points + fine * 100

        return points

    def on_receive(self, message):
        if isinstance(message, SiteResponse):
            self.on_site_record(message)

        if isinstance(message, SiteDeleteResponse):
            self.on_delete_site(message)

    def on_site_record(self, site):
        self.sites[site.id] = site

    def on_delete_site(self, message):
        del self.sites[message.id]

    def download_site(self, site):
        try:
            self.storage_proxy.update_site(UpdateSiteRequest(id=site.id, status=WatchStatus.IN_PROGRESS))
            with urllib.request.urlopen(site.url) as f:
                html = f.read().decode('utf-8')
                logger.debug('Site {0} - {1} downloaded'.format(site.name, site.url))
                self.analytic_proxy.analyze_site(site, html)
        except Exception as e:
            logger.error("Error occurred: {0}".format(e))
            self.storage_proxy.update_site(UpdateSiteRequest(id=site.id, status=WatchStatus.ERROR))