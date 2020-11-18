import unittest
from analyze.actor import SiteAnalyticActor, parse_json_array
import pykka
import io
from site_storage.messages import SiteResponse, SaveSiteVersion, UpdateSiteRequest, SiteVersionResponse
import json
from site_storage.sсhema import WatchStatus, RegularCheck


def create_test_site_response(selectors=str(['.news', '#date']), keys=str(['зоопарк', 'шоссе', 'окно'])):
    return SiteResponse(
        id=1,
        name='Булочная',
        url='https://ru.wiktionary.org/wiki/boulangerie',
        keys=keys,
        selectors=selectors,
        last_watch=None,
        count_watches=0,
        status=WatchStatus.NEW,
        regular_check=RegularCheck.ONCE_DAY
    )


def read_test_page(page_name):
    with io.open(page_name, 'r') as test_page:
        html = test_page.readlines()
        if isinstance(html, list):
            html = ' '.join(html)

        return html


class TestAnalyzerActor(SiteAnalyticActor):
    def __init__(self, storage_proxy, asserter):
        super().__init__(storage_proxy)
        self.asserter = asserter

    def test_find_watch_fragments(self):
        try:
            html = read_test_page('test/test_page.html')
            site = create_test_site_response()
            expected_result = {
                ".news": 'Из зоопарка сбежал жираф В ***районе открыли новую школу Закончен ремонт 20 километра дороги шоссе Кострома-Рязань',
                "#date": '18:09:13 2020-11-18'}
            result = self._find_watch_fragments(site, html)
            self.asserter.assertEqual(result, expected_result)
            return True
        except:
            return False

    def test_find_watch_fragments_incorrect_page(self):
        try:
            html = read_test_page('test/incorrect_page.html')
            site = create_test_site_response()
            expected_result = {}
            result = self._find_watch_fragments(site, html)
            self.asserter.assertEqual(result, expected_result)
            return True
        except:
            return False

    def test_find_key_matches_new(self):
        try:
            site = create_test_site_response()
            content = 'Из зоопарка сбежал жираф В ***районе открыли новую школу Закончен ремонт 20 километра дороги шоссе Кострома-Рязань'
            result = self._find_key_matches(site, content.split())

            self.asserter.assertEqual(len(result), 2)
            self.asserter.assertEqual(result[0].name, 'зоопарк')
            self.asserter.assertEqual(result[1].name, 'шоссе')
            return True
        except:
            return False

    def test_find_key_matches_changed(self):
        try:
            site = create_test_site_response()
            content = 'Из зоопарка сбежал жираф В ***районе открыли новую школу Закончен ремонт 20 километра дороги шоссе Кострома-Рязань'
            result = self._find_key_matches(site, content.split(), 11, 16)

            self.asserter.assertEqual(len(result), 1)
            self.asserter.assertEqual(result[0].name, 'шоссе')
            return True
        except:
            return False

    def test_find_key_matches_change_incorrect_index(self):
        try:
            site = create_test_site_response()
            content = 'Из зоопарка сбежал жираф В ***районе открыли новую школу Закончен ремонт 20 километра дороги шоссе Кострома-Рязань'
            result = self._find_key_matches(site, content.split(), 140, 150)

            self.asserter.assertEqual(len(result), 0)
            return True
        except:
            return False

    def test_compare_versions(self):
        try:
            site = create_test_site_response()
            old_content = {
                ".news": 'Новое слово: зоопарк'}
            new_content = {
                ".news": 'Новое слово: шоссе'}

            differences, keys = self._compare_versions(site, new_content, old_content)

            differences = differences['.news']
            keys = keys['.news']
            self.asserter.assertEqual(len(differences), 1)
            self.asserter.assertEqual(differences[0].type, 'replace')
            self.asserter.assertEqual(differences[0].start, 13)
            self.asserter.assertEqual(differences[0].end, 18)
            self.asserter.assertEqual(len(keys), 1)
            self.asserter.assertEqual(keys[0].name, 'шоссе')
            return True
        except:
            return False

    def test_analyze_site(self):
        try:
            class MockStorage(pykka.ThreadingActor, unittest.TestCase):
                def __init__(self, asserter):
                    super().__init__()
                    self.asserter = asserter
                    self.successful = 0

                def save_site_version(self, site_version):
                    self.asserter.assertEqual(type(site_version), SaveSiteVersion)
                    self.asserter.assertEqual(site_version.site_id, site.id)
                    self.asserter.assertEqual(site_version.count_changes, 3)
                    differences = json.loads(site_version.differences)
                    keys = json.loads(site_version.match_keys)

                    news_diff = differences['.news']
                    self.asserter.assertEqual(len(news_diff), 2)
                    self.asserter.assertEqual(news_diff[0]['type'], 'insert')
                    self.asserter.assertEqual(news_diff[0]['start'], 0)
                    self.asserter.assertEqual(news_diff[0]['end'], 24)

                    self.asserter.assertEqual(news_diff[1]['type'], 'insert')
                    self.asserter.assertEqual(news_diff[1]['start'], 57)
                    self.asserter.assertEqual(news_diff[1]['end'], 114)

                    date_diff = differences['#date']
                    self.asserter.assertEqual(date_diff[0]['type'], 'insert')
                    self.asserter.assertEqual(date_diff[0]['start'], 0)
                    self.asserter.assertEqual(date_diff[0]['end'], 19)

                    news_keys = keys['.news']
                    self.asserter.assertEqual(len(news_keys), 2)
                    self.asserter.assertEqual(news_keys[0]['name'], 'зоопарк')
                    self.asserter.assertEqual(news_keys[0]['start'], 3)
                    self.asserter.assertEqual(news_keys[0]['end'], 10)

                    self.asserter.assertEqual(news_keys[1]['name'], 'шоссе')
                    self.asserter.assertEqual(news_keys[1]['start'], 93)
                    self.asserter.assertEqual(news_keys[1]['end'], 98)

                    date_keys = keys['#date']
                    self.asserter.assertEqual(len(date_keys), 0)
                    self.successful +=1

                def update_site(self, site_record):
                    self.asserter.assertEqual(type(site_record), UpdateSiteRequest)
                    self.asserter.assertEqual(site_record.id, site.id)
                    self.asserter.assertEqual(site_record.status, WatchStatus.WATCHED)
                    self.asserter.assertEqual(site_record.count_watches, 1)
                    self.asserter.assertEqual(site_record.url, None)
                    self.asserter.assertEqual(site_record.name, None)
                    self.asserter.assertEqual(site_record.keys, None)
                    self.asserter.assertEqual(site_record.selectors, None)
                    self.asserter.assertEqual(site_record.regular_check, None)
                    self.successful += 1

                def result(self):
                    return self.successful == 2


                def get_last_site_version(self, site_id):
                    return SiteVersionResponse(id=1,
                                               site_id=site_id,
                                               content='{".news": "В ***районе открыли новую школу"}',
                                               differences='{}',
                                               match_keys='{}',
                                               count_changes=0,
                                               count_match_keys=0,
                                               created_at=None)

            self.storage_proxy = MockStorage.start(self.asserter).proxy()
            site = create_test_site_response()
            html = read_test_page('test/test_page.html')
            self.analyze_site(site, html)
            result = self.storage_proxy.result().get()
            self.asserter.assertEqual(result, True)
            return True
        except:
            return False


    def test_analyze_site_incorrect_site_argument(self):
        site = "Это просто строка"
        html = read_test_page('test/test_page.html')
        with self.asserter.assertRaises(Exception):
            self.analyze_site(site, html)
        return True

    def test_analyze_site_incorrect_html_argument(self):
        try:
            class MockStorage(pykka.ThreadingActor, unittest.TestCase):
                def __init__(self, asserter):
                    super().__init__()
                    self.asserter = asserter
                    self.successful = 0

                def update_site(self, site_record):
                    self.asserter.assertEqual(type(site_record), UpdateSiteRequest)
                    self.asserter.assertEqual(site_record.id, site.id)
                    self.asserter.assertEqual(site_record.status, WatchStatus.ERROR)
                    self.asserter.assertEqual(site_record.count_watches, None)
                    self.asserter.assertEqual(site_record.url, None)
                    self.asserter.assertEqual(site_record.name, None)
                    self.asserter.assertEqual(site_record.keys, None)
                    self.asserter.assertEqual(site_record.selectors, None)
                    self.asserter.assertEqual(site_record.regular_check, None)
                    self.successful += 1

                def result(self):
                    return self.successful == 1


            self.storage_proxy = MockStorage.start(self.asserter).proxy()
            site = create_test_site_response()
            html = ['один', 'два', 'три']
            self.analyze_site(site, html)
            result = self.storage_proxy.result().get()
            self.asserter.assertEqual(result, True)
            return True
        except:
            return False

    def test_analyze_site_incorrect_content_attribute(self):
        try:
            class MockStorage(pykka.ThreadingActor, unittest.TestCase):
                def __init__(self, asserter):
                    super().__init__()
                    self.asserter = asserter
                    self.successful = 0

                def update_site(self, site_record):
                    self.asserter.assertEqual(type(site_record), UpdateSiteRequest)
                    self.asserter.assertEqual(site_record.id, site.id)
                    self.asserter.assertEqual(site_record.status, WatchStatus.ERROR)
                    self.asserter.assertEqual(site_record.count_watches, None)
                    self.asserter.assertEqual(site_record.url, None)
                    self.asserter.assertEqual(site_record.name, None)
                    self.asserter.assertEqual(site_record.keys, None)
                    self.asserter.assertEqual(site_record.selectors, None)
                    self.asserter.assertEqual(site_record.regular_check, None)
                    self.successful += 1

                def result(self):
                    return self.successful == 1

                def get_last_site_version(self, site_id):
                    return SiteVersionResponse(id=1,
                                               site_id=site_id,
                                               content="В ***районе открыли новую школу",
                                               differences='{}',
                                               match_keys='{}',
                                               count_changes=0,
                                               count_match_keys=0,
                                               created_at=None)

            self.storage_proxy = MockStorage.start(self.asserter).proxy()
            site = create_test_site_response()
            html = read_test_page('test/test_page.html')
            self.analyze_site(site, html)
            result = self.storage_proxy.result().get()
            self.asserter.assertEqual(result, True)
            return True
        except:
            return False


class TestAnalyzer(unittest.TestCase):
    def setUp(self):
        # self.mock_storage_proxy = MockStorage.start().proxy()
        self.actor_proxy = TestAnalyzerActor.start(storage_proxy=None, asserter=self).proxy()

    def tearDown(self):
        pykka.ActorRegistry.stop_all()

    def test_parse_json_array(self):
        test_array = ['мама', 'мыла', 'раму']
        test_array_str = str(test_array)
        result = parse_json_array(test_array_str)
        self.assertEqual(result, test_array)

    def test_parse_json_array_incorrect_str(self):
        test_array_str = '[%мама\ %мыла 451$ раму'
        result = parse_json_array(test_array_str)
        self.assertEqual(result, [test_array_str])

    def test_parse_json_array_incorrect_type_of_argument(self):
        test_array = ['мама', 'мыла', 'раму']
        result = parse_json_array(test_array)
        self.assertEqual(result, test_array)

    def test_find_watch_fragments(self):
        result = self.actor_proxy.test_find_watch_fragments().get()
        self.assertEqual(result, True)

    def test_find_watch_fragments_incorrect_page(self):
        result = self.actor_proxy.test_find_watch_fragments_incorrect_page().get()
        self.assertEqual(result, True)

    def test_find_key_matches_new(self):
        result = self.actor_proxy.test_find_key_matches_new().get()
        self.assertEqual(result, True)

    def test_find_key_matches_new(self):
        result = self.actor_proxy.test_find_key_matches_new().get()
        self.assertEqual(result, True)

    def test_find_key_matches_changed(self):
        result = self.actor_proxy.test_find_key_matches_changed().get()
        self.assertEqual(result, True)

    def test_find_key_matches_change_incorrect_index(self):
        result = self.actor_proxy.test_find_key_matches_change_incorrect_index().get()
        self.assertEqual(result, True)

    def test_compare_versions(self):
        result = self.actor_proxy.test_compare_versions().get()
        self.assertEqual(result, True)

    def test_analyze_site(self):
        result = self.actor_proxy.test_analyze_site().get()
        self.assertEqual(result, True)

    def test_analyze_site_incorrect_site_argument(self):
        result = self.actor_proxy.test_analyze_site_incorrect_site_argument().get()
        self.assertEqual(result, True)

    def test_analyze_site_incorrect_html_argument(self):
        result = self.actor_proxy.test_analyze_site_incorrect_html_argument().get()
        self.assertEqual(result, True)

    def test_analyze_site_incorrect_content_attribute(self):
        result = self.actor_proxy.test_analyze_site_incorrect_content_attribute().get()
        self.assertEqual(result, True)


if __name__ == "__main__":
    unittest.main()