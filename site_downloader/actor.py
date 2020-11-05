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

    def __init__(self, storage_proxy):
        super().__init__()
        self.pause_handle = False
        self.storage_proxy = storage_proxy
        self.sites = dict()
        self.queue = list()
        self.create_queue()

    def on_start(self):
        self.handle_process = Process(target=self.handle())
        self.handle_process.start()

    def handle(self):
        self.last_update = datetime.datetime.now()
        while True:
            if self.pause_handle:
                continue

            current_time = datetime.datetime.now()
            difference = current_time - self.last_update

            if difference.seconds >= 60:
                self.recalculate_queue()
                self.last_update = datetime.datetime.now()

            if len(self.queue) > 0:
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
        for site in self.sites.values():
            points = self.calculate_priority(site)
            if points > 0:
                self.queue.append((points, site))
        self.queue.sort(key=lambda x: x[0])

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

        if isinstance(message, SiteDeleteResponse):
            self.on_delete_site(message)

    def on_site_record(self, site):
        self.pause_handle = True
        if site.id not in self.sites:
            points = self.calculate_priority(site)
            self.queue.append((points, site))
            self.queue.sort(reverse=True, key=lambda x: x[0])

        self.sites[site.id] = site
        self.pause_handle = False

    def on_delete_site(self, message):
        del self.sites[message.id]

    def download_site(self, site):
        try:
            site.status = WatchStatus.IN_PROGRESS
            self.storage_proxy.update_site(site)
            with urllib.request.urlopen(site.url) as f:
                html = f.read().decode('utf-8')
                print('site downloaded')
        except Exception as e:
            print(e)