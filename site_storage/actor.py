import pykka
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .sсhema import SiteConfig, engine, metadata
from .messages import SiteDeleteResponse, ResponseStatus


class SiteStorageActor(pykka.ThreadingActor):
    def __init__(self):
        super().__init__()
        self.Session = sessionmaker(bind=engine)

    def create_site_record(self, site):
        if not isinstance(site, SiteConfig):
            raise Exception("Not support such type")

        session = self.Session()
        session.add(site)
        session.commit()
        session.close()
        pykka.ActorRegistry.broadcast(site)


    def get_site_by_id(self, id):
        if not isinstance(id, int):
            raise Exception("Not support such type")

        session = self.Session()
        site = session.query(SiteConfig).filter_by(id=id).first()
        session.close()
        return site

    def get_sites(self):
        session = self.Session()
        all_sites = session.query(SiteConfig).all()
        session.close()
        return all_sites

    def delete_site(self, id):
        if not isinstance(id, int):
            raise Exception("Not support such type")

        session = self.Session()
        site = session.query(SiteConfig).filter_by(id=id).first()
        if site is None:
            response = SiteDeleteResponse(
                "Site with id = {0} not found".format(id),
                ResponseStatus.error
            )
            session.close()
            return response
        else:
            session.delete(site)
            session.commit()

            pykka.ActorRegistry.broadcast(SiteDeleteResponse(
                "Site was deleted",
                ResponseStatus.success,
                site.id
            ))

    def update_site(self, site):
        session = self.Session()
        session.add(site)
        session.commit()
        session.close()
        pykka.ActorRegistry.broadcast(site)
