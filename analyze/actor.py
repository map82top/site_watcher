import pykka
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
from site_storage.messages import SaveSiteVersion, UpdateSiteRequest
from site_storage.sсhema import WatchStatus
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


@dataclass
class MatchKey:
    name: str
    start: int
    end: int


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)


class SitaAnalyticActor(pykka.ThreadingActor):
    def __init__(self, storage_proxy):
        super().__init__()
        self.storage_proxy = storage_proxy

    def analyze_site(self, site, html):
        try:
            logger.debug('Start analyze {0}'.format(site.name))
            soup = BeautifulSoup(html, 'lxml')
            base_content = ''
            logger.debug('HTML code is parsed')
            for tag in soup.find_all(['div', 'p', 'h1', 'h2', 'li']):
                base_content = base_content + ' ' + tag.text
            count_uppercase = 0
            for uppercase in re.finditer("[^A-ZA-Я]{1}[A-ZA-Я]{1}", base_content):
                base_content = base_content[0: uppercase.start() + count_uppercase + 1] + ' ' + base_content[uppercase.end() + count_uppercase - 1: len(base_content)]
                count_uppercase = count_uppercase + 1

            last_version = self.storage_proxy.get_last_site_version(site.id).get()
            differences = []
            keys = []

            if last_version is not None:
                differences, keys = self.__compare_versions__(site, base_content, last_version.content)
            else:
                keys = self.__find_key_matches__(site, base_content)

            site_version = SaveSiteVersion(
                site_id=site.id,
                content=base_content,
                differences=json.dumps(differences, cls=EnhancedJSONEncoder, ensure_ascii=False),
                match_keys=json.dumps(keys, cls=EnhancedJSONEncoder, ensure_ascii=False),
                count_changes=len(differences),
                count_match_keys=len(keys)
            )

            self.storage_proxy.update_site(UpdateSiteRequest(
                id=site.id,
                status=WatchStatus.WATCHED,
                count_watches=site.count_watches+1,
                last_watch=datetime.now()
            ))

            self.storage_proxy.save_site_version(site_version)
        except Exception as e:
            logger.error("Error occurred: {0}".format(e))
            self.storage_proxy.update_site(UpdateSiteRequest(id=site.id, status=WatchStatus.ERROR))

    def __compare_versions__(self, site, new_version, last_version):
        differences = []
        keys = []
        matcher = SequenceMatcher(lambda x: x == " ", last_version, new_version)
        for type_change, i1, i2, j1, j2 in matcher.get_opcodes():
            if type_change in ('replace', 'insert'):
                keys = keys + self.__find_key_matches__(site, new_version, j1, j2)

                logger.debug('find difference {0} - {1}'.format(last_version[i1:i2], new_version[j1:j2]))
                differences.append(Difference(type_change, j1, j2))

        return differences, keys

    def __find_key_matches__(self, site, content, start=0, end=None):
        keys = []
        site_keys = self.__parse_site_keys__(site.keys)
        if end is None:
            end = len(content)

        for key in site_keys:
            for key_word in re.finditer(key, content[start:end], re.IGNORECASE):
                keys.append(MatchKey(name=key, start=key_word.start() + start, end=key_word.end() + start))

        return keys

    def __parse_site_keys__(self, keys: str):
        return [split_chunk for split_chunk in re.split(r'[\[\]\',]', keys) if split_chunk.strip() != '']
