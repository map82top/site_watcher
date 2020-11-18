import unittest
from site_downloader.actor import SiteDownloaderActor
import pykka
import io
from site_storage.messages import SiteResponse, SaveSiteVersion, UpdateSiteRequest, SiteVersionResponse
import json
from site_storage.sсhema import WatchStatus, RegularCheck
import datetime


class MockStorage(pykka.ThreadingActor):
    def subscribe_on_site_update(self, subscription):
        pass

    def get_sites(self):
        return []


def create_test_site_response(id=1, name='Сайт', url='https://ru.wiktionary.org/wiki/boulangerie',
                            selectors=str(['.news', '#date']), keys=str(['зоопарк', 'шоссе', 'окно']),
                            last_watch=None, status=WatchStatus.NEW, regular_check=RegularCheck.ONCE_HOUR):
    return SiteResponse(
        id=id,
        name=name,
        url=url,
        keys=keys,
        selectors=selectors,
        last_watch=last_watch,
        count_watches=0,
        status=status,
        regular_check=regular_check
    )


class TestSiteDownloaderActor(SiteDownloaderActor):
    def __init__(self, storage_proxy, asserter):
        super().__init__(storage_proxy, None)
        self.asserter = asserter

    def test_create_queue(self):
        try:
            class TestMockStorage(pykka.ThreadingActor):
                def get_sites(self):
                    return [create_test_site_response(id=1, name='Сайт1', regular_check=RegularCheck.TWICE_DAY),
                            create_test_site_response(id=2, name='Сайт2', regular_check=RegularCheck.TWICE_HOUR)]

            self.handle_process.stop()
            self.storage_proxy = TestMockStorage.start().proxy()
            self._create_queue()
            self.asserter.assertEqual(len(self.sites), 2)
            self.asserter.assertEqual(len(self.queue), 2)
            first_site = self.queue.pop()
            self.asserter.assertEqual(first_site[0], 11000)
            second_site = self.queue.pop()
            self.asserter.assertEqual(second_site[0], 10125)
            return True
        except:
            return False

    def test_create_queue_exception(self):
        try:
            class TestMockStorage(pykka.ThreadingActor):
                def get_sites(self):
                    return ["Сайт",
                            create_test_site_response(id=2, name='Сайт2', regular_check=RegularCheck.TWICE_HOUR)]

            self.handle_process.stop()
            self.storage_proxy = TestMockStorage.start().proxy()
            with self.asserter.assertRaises(Exception):
                self._create_queue()

            return True
        except:
            return False

    def test_recalculate_priority(self):
        try:
            class TestMockStorage(pykka.ThreadingActor):
                def get_sites(self):
                    return [create_test_site_response(id=1, name='Сайт1', regular_check=RegularCheck.TWICE_DAY),
                            create_test_site_response(id=2, name='Сайт2', regular_check=RegularCheck.TWICE_HOUR)]

            self.handle_process.stop()
            self.storage_proxy = TestMockStorage.start().proxy()
            self._create_queue()
            self.asserter.assertEqual(len(self.sites), 2)
            self.asserter.assertEqual(len(self.queue), 2)
            first_site = self.queue.pop()
            self.asserter.assertEqual(first_site[0], 11000)
            second_site = self.queue.pop()
            self.asserter.assertEqual(second_site[0], 10125)

            self.sites[2].status = WatchStatus.WATCHED
            self.sites[2].last_watch = str(datetime.datetime.now() - datetime.timedelta(minutes=20))
            self._recalculate_queue()

            self.asserter.assertEqual(len(self.sites), 2)
            self.asserter.assertEqual(len(self.queue), 1)
            first_site = self.queue.pop()
            self.asserter.assertEqual(first_site[0], 10125)

            return True
        except:
            return False

    def test_download_site(self):
        try:
            class TestMockStorage(pykka.ThreadingActor):
                def __init__(self, asserter):
                    super().__init__()
                    self.asserter = asserter
                    self.successful = 0

                def update_site(self, update_site):
                    self.asserter.assertEqual(type(update_site), UpdateSiteRequest)
                    self.asserter.assertEqual(update_site.id, site.id)
                    self.asserter.assertEqual(update_site.status, WatchStatus.IN_PROGRESS)
                    self.successful += 1

                def result(self):
                    return self.successful == 1

            class TestMockAnalyzer(pykka.ThreadingActor):
                def __init__(self, asserter):
                    super().__init__()
                    self.asserter = asserter
                    self.successful = 0

                def analyze_site(self, site, html):
                    self.asserter.assertEqual(type(site), SiteResponse)
                    self.asserter.assertEqual(type(html), str)
                    # self.asserter.assertEqual(update_site.status, WatchStatus)
                    self.successful += 1

                def result(self):
                    return self.successful == 1

            self.handle_process.stop()
            self.storage_proxy = TestMockStorage.start(self.asserter).proxy()
            self.analytic_proxy = TestMockAnalyzer.start(self.asserter).proxy()
            site = create_test_site_response()
            self._download_site(site)
            self.asserter.assertEqual(self.storage_proxy.result().get(), 1)
            self.asserter.assertEqual(self.analytic_proxy.result().get(), 1)
            return True
        except:
            return False

    def test_download_site_exception(self):
        try:
            class TestMockStorage(pykka.ThreadingActor):
                def __init__(self, asserter):
                    super().__init__()
                    self.asserter = asserter
                    self.successful = 0

                def update_site(self, update_site):
                    self.asserter.assertEqual(type(update_site), UpdateSiteRequest)
                    self.asserter.assertEqual(update_site.id, site.id)
                    if self.successful == 0:
                        self.asserter.assertEqual(update_site.status, WatchStatus.IN_PROGRESS)
                    else:
                        self.asserter.assertEqual(update_site.status, WatchStatus.ERROR)
                    self.successful += 1

                def result(self):
                    return self.successful == 2

            self.handle_process.stop()
            self.storage_proxy = TestMockStorage.start(self.asserter).proxy()
            site = create_test_site_response(url='https://test_site.html')
            self._download_site(site)
            self.asserter.assertEqual(self.storage_proxy.result().get(), True)
            return True
        except:
            return False

    def test_calculate_priority_not_watch(self):
        try:
            site = create_test_site_response()
            priority = self._calculate_priority(site)
            self.asserter.assertEqual(priority, 10500)
            return True
        except:
            return False

    def test_calculate_priority_watch_two_hour_ago(self):
        try:
            last_watch = datetime.datetime.now() - datetime.timedelta(minutes=120)
            site = create_test_site_response(last_watch=str(last_watch))
            priority = self._calculate_priority(site)
            self.asserter.assertEqual(priority, 6500)
            return True
        except:
            return False

    def test_calculate_priority_time_not_inspire(self):
        try:
            last_watch = datetime.datetime.now() - datetime.timedelta(minutes=30)
            site = create_test_site_response(last_watch=str(last_watch))
            priority = self._calculate_priority(site)
            self.asserter.assertEqual(priority, -1)
            return True
        except:
            return False


class TestSiteDownloader(unittest.TestCase):
    def setUp(self):
        self.mock_storage_proxy = MockStorage.start().proxy()
        self.actor_proxy = TestSiteDownloaderActor.start(storage_proxy=self.mock_storage_proxy, asserter=self).proxy()

    def tearDown(self):
        pykka.ActorRegistry.stop_all()

    def test_create_queue(self):
        result = self.actor_proxy.test_create_queue().get()
        self.assertEqual(result, True)

    def test_create_queue_exception(self):
        result = self.actor_proxy.test_create_queue_exception().get()
        self.assertEqual(result, True)

    def test_caluclate_priority_not_watch(self):
        result = self.actor_proxy.test_calculate_priority_not_watch().get()
        self.assertEqual(result, True)

    def test_caluclate_priority_watch_two_hour_ago(self):
        result = self.actor_proxy.test_calculate_priority_watch_two_hour_ago().get()
        self.assertEqual(result, True)

    def test_caluclate_priority_time_not_inspire(self):
        result = self.actor_proxy.test_calculate_priority_time_not_inspire().get()
        self.assertEqual(result, True)

    def test_recalculate_priority(self):
        result = self.actor_proxy.test_recalculate_priority().get()
        self.assertEqual(result, True)

    def test_download_site(self):
        result = self.actor_proxy.test_download_site().get()
        self.assertEqual(result, True)

    def test_download_site_exception(self):
        result = self.actor_proxy.test_download_site_exception().get()
        self.assertEqual(result, True)


if __name__ == "__main__":
    unittest.main()