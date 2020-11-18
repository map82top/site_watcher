import pykka
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
from site_storage.messages import SaveSiteVersion, UpdateSiteRequest, SiteResponse
from site_storage.sсhema import WatchStatus
from site_storage.encoders import AlchemyEncoder
from dataclasses import dataclass, is_dataclass, asdict
import re
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Difference:
    type: str
    start: int
    end: int

    @staticmethod
    def convert_to_difference(selector_new_content, type, start, end):
        before_start_len = 0
        change_space_len = 0
        for word in selector_new_content[:start]:
            before_start_len += len(word) + 1

        for word in selector_new_content[start:end]:
            change_space_len += len(word) + 1

        return Difference(type, before_start_len, before_start_len + change_space_len - 1)


@dataclass
class MatchKey:
    name: str
    start: int
    end: int


def parse_json_array(json_array: str):
    if not isinstance(json_array, str):
        json_array = str(json_array)
    return [split_chunk for split_chunk in re.split(r"\[\'|\'\]|,|\'", json_array) if split_chunk.strip() != '']

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)


class SiteAnalyticActor(pykka.ThreadingActor):
    def __init__(self, storage_proxy):
        super().__init__()
        self.storage_proxy = storage_proxy

    def on_stop(self):
        logger.info('Analyzer stopped')

    def analyze_site(self, site, html):
        if not isinstance(site, SiteResponse):
            raise Exception('Incorrect site argument type')

        if not isinstance(html, str):
            self._send_analyze_error(site, Exception('Incorrect html argument type'))
            return

        try:
            logger.debug('Start analyze {0}'.format(site.name))
            watch_fragments = self._find_watch_fragments(site, html)
            differences = {}
            keys = {}

            last_version = self.storage_proxy.get_last_site_version(site.id).get()

            if last_version is not None:
                last_version.content = json.loads(last_version.content)
                differences, keys = self._compare_versions(site, watch_fragments,  last_version.content)
            else:
                for selector in watch_fragments:
                    keys[selector] = keys.get(selector, []) + self._find_key_matches(site, watch_fragments[selector])

            self._send_analyze_result(site, watch_fragments, differences, keys)
        except Exception as e:
            self._send_analyze_error(site, e)

    def _send_analyze_error(self, site, error):
        logger.error("Error occurred: {0}".format(error))
        self.storage_proxy.update_site(UpdateSiteRequest(id=site.id, status=WatchStatus.ERROR))

    def _find_watch_fragments(self, site, html):
        soup = BeautifulSoup(html, 'lxml')
        watch_fragments = {}
        selectors = parse_json_array(site.selectors)

        for selector in selectors:
            for tag in soup.select(selector):
                if selector not in watch_fragments:
                    watch_fragments[selector] = tag.text
                else:
                    watch_fragments[selector] += ' ' + tag.text

        return watch_fragments

    def _compare_versions(self, site, new_version, last_version):
        differences = {}
        keys = {}

        if new_version is None or last_version is None:
            raise Exception('Versions can`t be None')

        for selector in new_version:
            selector_new_content = new_version[selector].split()
            selector_old_content = last_version.get(selector, '').split()

            matcher = SequenceMatcher(None, selector_old_content, selector_new_content)
            for type_change, i1, i2, j1, j2 in matcher.get_opcodes():
                if type_change in ('replace', 'insert'):
                    difference = Difference.convert_to_difference(selector_new_content, type_change, j1, j2)
                    differences[selector] = differences.get(selector, []) + [difference]
                    keys[selector] = keys.get(selector, []) + self._find_key_matches(site, selector_new_content, j1, j2, difference.start)
        return differences, keys

    def _find_key_matches(self, site: SiteResponse, content: list, start=0, end=None, start_position=0):
        keys = []
        site_keys = parse_json_array(site.keys)
        if end is None:
            end = len(content)

        for key in site_keys:
            for key_word in re.finditer(key, ' '.join(content[start:end]), re.IGNORECASE):
                keys.append(MatchKey(name=key, start=key_word.start() + start_position, end=key_word.end() + start_position))

        return keys

    def _send_analyze_result(self, site, watch_fragments, differences, keys):
        count_keys = 0
        for key in keys:
            count_keys += len(keys[key])

        count_differences = 0
        for diff in differences:
            count_differences += len(differences[diff])

        site_version = SaveSiteVersion(
            site_id=site.id,
            content=json.dumps(watch_fragments, cls=EnhancedJSONEncoder, ensure_ascii=False),
            differences=json.dumps(differences, cls=EnhancedJSONEncoder, ensure_ascii=False),
            match_keys=json.dumps(keys, cls=EnhancedJSONEncoder, ensure_ascii=False),
            count_changes=count_differences,
            count_match_keys=count_keys
        )

        self.storage_proxy.update_site(
            UpdateSiteRequest(
                id=site.id,
                status=WatchStatus.WATCHED,
                count_watches=site.count_watches + 1,
                last_watch=datetime.now()
            )
        )

        self.storage_proxy.save_site_version(site_version)
