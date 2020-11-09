import pykka
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .sсhema import Site, SiteVersion, engine, metadata
from .messages import SiteDeleteResponse, ResponseStatus, \
    SiteResponse, SiteDeleteRequest, UpdateSiteRequest, CreateSiteRequest, SubscribeOnSiteUpdates, \
    SiteVersionResponse, SaveSiteVersion, SiteCreateResponse, SiteUpdateResponse, SubscribeOnVersionsUpdates
from datetime import datetime

logger = logging.getLogger(__name__)

def __format_datetime__(date:datetime):
    if date is None:
        return None
    else:
        return date.replace(microsecond=0).isoformat(' ')


class SiteStorageActor(pykka.ThreadingActor):
    def __init__(self):
        super().__init__()
        self.Session = sessionmaker(bind=engine, expire_on_commit=True)
        self.site_subscribers = []
        self.version_subscribers = []

    def create_site_record(self, site):
        try:
            if not isinstance(site, CreateSiteRequest):
                raise Exception("Not support such type")

            session = self.Session()
            site_model = Site(
                site.name,
                site.url,
                site.regular_check,
                site.keys
            )
            session.add(site_model)
            session.commit()
            site_create_response = self.__convert_to_site_response__(site_model)

            self.__send_all_subscibers__(site_create_response, self.site_subscribers)
            return SiteCreateResponse("{0} site is created".format(site_create_response.name), ResponseStatus.success)
        except Exception as e:
            logger.error("Error occurred: {0}".format(e))
            return SiteCreateResponse("Error occurred: {0}".format(e), ResponseStatus.error)

    def get_site_by_id(self, id):
        try:
            if not isinstance(id, int):
                raise Exception("Not support such type")

            session = self.Session()
            site = session.query(Site).filter_by(id=id).first()
            return self.__convert_to_site_response__(site)
        except Exception as e:
            logger.error("Error occurred: {0}".format(e))

    def __convert_to_site_response__(self, site):
        return SiteResponse(
            id=site.id,
            name=site.name,
            url=site.url,
            keys=site.keys,
            last_watch=__format_datetime__(site.last_watch),
            count_watches=site.count_watches,
            regular_check=site.regular_check,
            status=site.status,
            created_at=__format_datetime__(site.created_at)
        )

    def get_sites(self):
        try:
            session = self.Session()
            all_sites = session.query(Site).all()
            all_sites_response = []

            for site in all_sites:
                all_sites_response.append(self.__convert_to_site_response__(site))

            return all_sites_response
        except Exception as e:
            logger.error("Error occurred: {0}".format(e))


    def delete_site(self, delete_request):
        try:
            if not isinstance(delete_request, SiteDeleteRequest):
                raise Exception("Not support such type")

            session = self.Session()
            site = session.query(Site).filter_by(id=delete_request.id).first()
            if site is None:
                return SiteDeleteResponse(
                    "Site with id = {0} not found".format(id),
                    ResponseStatus.error
                )
            else:
                for version in session.query(SiteVersion).filter_by(site_id=delete_request.id).all():
                    session.delete(version)

                session.delete(site)
                response = SiteDeleteResponse(
                    "Site was deleted",
                    ResponseStatus.success,
                    site.id
                )
                session.commit()
                self.__send_all_subscibers__(response, self.site_subscribers)
        except Exception as e:
            logger.error("Error occurred: {0}".format(e))
            return SiteDeleteResponse(
                    "Error occurred: {0}".format(e),
                    ResponseStatus.error
            )

    def update_site(self, site):
        try:
            if not isinstance(site, UpdateSiteRequest):
                raise Exception("Not support such type")

            if site is None:
                return SiteUpdateResponse(
                    "Site with id = {0} not found".format(id),
                    ResponseStatus.error
                )

            session = self.Session()
            site_model = session.query(Site).filter_by(id=site.id).first()

            if site.keys is not None:
                site_model.keys = site.keys

            if site.name is not None:
                site_model.name = site.name

            if site.url is not None:
                site_model.url = site.url

            if site.last_watch is not None:
                site_model.last_watch = site.last_watch

            if site.count_watches is not None:
                site_model.count_watches = site.count_watches

            if site.regular_check is not None:
                site_model.regular_check = site.regular_check

            if site.status is not None:
                site_model.status = site.status

            if site.created_at is not None:
                site_model.created_at = site.created_at

            session.add(site_model)
            session.commit()
            self.__send_all_subscibers__(self.__convert_to_site_response__(site_model), self.site_subscribers)
            return SiteUpdateResponse("Site record is updated", ResponseStatus.success)
        except Exception as e:
            logger.error("Error occurred: {0}".format(e))
            return SiteUpdateResponse("Error occurred: {0}".format(e), ResponseStatus.error)

    def __send_all_subscibers__(self, message, subscribers):
        for subscriber in subscribers:
            subscriber.actor_proxy.tell(message)

    def subscribe_on_site_update(self, subscription):
        try:
            if not isinstance(subscription, SubscribeOnSiteUpdates):
                raise Exception("Not support such type")

            self.site_subscribers.append(subscription)
        except Exception as e:
            logger.error("Error occurred: {0}".format(e))

    def subscribe_on_site_versions_update(self, subscription):
        try:
            if not isinstance(subscription, SubscribeOnVersionsUpdates):
                raise Exception("Not support such type")

            self.version_subscribers.append(subscription)
        except Exception as e:
            logger.error("Error occurred: {0}".format(e))

    def save_site_version(self, message):
        try:
            if not isinstance(message, SaveSiteVersion):
                raise Exception("Not support such type")

            session = self.Session()
            site_version = SiteVersion(
                site_id=message.site_id,
                content=message.content,
                differences=message.differences,
                match_keys=message.match_keys,
                count_changes=message.count_changes,
                count_match_keys=message.count_match_keys
            )

            session.add(site_version)
            session.commit()
            self.__send_all_subscibers__(self.__convert_to_site_version_response__(site_version), self.version_subscribers)
        except Exception as e:
            logger.error("Error occurred: {0}".format(e))

    def get_last_site_version(self, site_id):
        try:
            if not isinstance(site_id, int):
                raise Exception("Not support such type")

            session = self.Session()
            last_site_version = session.query(SiteVersion).filter_by(site_id=site_id).order_by(SiteVersion.created_at.desc()).limit(1).first()
            return self.__convert_to_site_version_response__(last_site_version)
        except Exception as e:
            logger.error("Error occurred: {0}".format(e))

    def get_all_site_versions(self, site_id):
        try:
            if not isinstance(site_id, int):
                raise Exception("Not support such type")

            session = self.Session()
            all_last_site_versions = session.query(SiteVersion).filter_by(site_id=site_id).all()
            all_last_site_version_responses = []
            for site_version in all_last_site_versions:
                all_last_site_version_responses.append(self.__convert_to_site_version_response__(site_version))

            return all_last_site_version_responses
        except Exception as e:
            logger.error("Error occurred: {0}".format(e))

    def __convert_to_site_version_response__(self, site_version):
        if site_version is None:
            return None
        else:
            return SiteVersionResponse(
                id=site_version.id,
                site_id=site_version.site_id,
                content=site_version.content,
                differences=site_version.differences,
                match_keys=site_version.match_keys,
                created_at=__format_datetime__(site_version.created_at),
                count_match_keys=site_version.count_match_keys,
                count_changes=site_version.count_changes
            )