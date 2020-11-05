import pykka
from site_storage.sсhema import SiteConfig, RegularCheck, WatchStatus
from site_storage.messages import SiteDeleteResponse
import os
import datetime
import urllib.request
from multiprocessing import Process
import time


class SiteDownloaderActor(pykka.ThreadingActor):
    point_dict = {
        RegularCheck.TWICE_HOUR: 1000,
        RegularCheck.ONCE_HOUR: 500,
        RegularCheck.FOUR_TIMES_DAY: 250,
        RegularCheck.TWICE_DAY: 125,
        RegularCheck.ONCE_DAY: 100
    }

    regular_check_duration = {
        RegularCheck.TWICE_HOUR: 30,
        RegularCheck.ONCE_HOUR: 60,
        RegularCheck.FOUR_TIMES_DAY: 360,
        RegularCheck.TWICE_DAY: 720,
        RegularCheck.ONCE_DAY: 1440
    }

    recalculating = False

    def __init__(self, storage_proxy):
        super().__init__()
        self.storage_proxy = storage_proxy
        self.sites = dict()
        self.queue = list()
        self.create_queue()
        self.update_process = Process(target=self.recalculate_queue)
        self.update_process.start()
        self.download_process = Process(target=self.download_from_queue)
        self.download_process.start()

    def download_from_queue(self):
        while True:
            if self.recalculating:
                time.sleep(0.1)
                continue

            if len(self.queue) == 0:
                time.sleep(60)
                continue

            site = self.queue.pop()
            self.download_site(site[1])

    def create_queue(self):
        for site in self.storage_proxy.get_sites().get():
            self.sites[site.id] = site
            points = self.calculate_priority(site)
            if points > 0:
                self.queue.append((points, site))
        self.queue.sort(key=lambda x: x[0])

    def recalculate_queue(self):
        self.recalculating = True
        for site in self.sites.values():
            points = self.calculate_priority(site)
            if points > 0:
                self.queue.append((points, site))
        self.queue.sort(key=lambda x: x[0])
        self.recalculating = False
        time.sleep(60)

    def calculate_priority(self, site):
        points = 0

        points = points + self.point_dict[site.regular_check]
        if site.last_watch is None:
            points = points + 10000
        else:
            difference = datetime.datetime.now() - site.last_watch
            fine = difference.minute - self.regular_check_duration[site.reqular_check]
            if fine < 0:
                points = -1
            else:
                points = points + fine * 100

        return points

    def on_receive(self, message):
        if isinstance(message, SiteConfig):
            self.on_site_record(message)
            return

        if isinstance(message, SiteDeleteResponse):
            self.on_delete_site(message)
            return

    def on_site_record(self, site):
        if site.id not in self.sites:
            points = self.calculate_priority(site)
            self.queue.append((points, site))
            self.queue.sort(reverse=True, key=lambda x: x[0])

        self.sites[site.id] = site

    def on_delete_site(self, message):
        del self.sites[message.id]

    def download_site(self, site):
        site.status = WatchStatus.IN_PROGRESS
        self.storage_proxy.update_site(site)
        with urllib.request.urlopen(site.url) as f:
            html = f.read().decode('utf-8')
            print('site downloaded')