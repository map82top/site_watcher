import pykka
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .sсhema import SiteConfig, engine, metadata
from .messages import SiteDeleteResponse, ResponseStatus


class SiteStorageActor(pykka.ThreadingActor):
    def __init__(self):
        super().__init__()
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()

    def create_site_record(self, site):
        if not isinstance(site, SiteConfig):
            raise Exception("Not support such type")

        self.session.add(site)
        self.session.commit()
        pykka.ActorRegistry.broadcast(site)

    def get_site_by_id(self, id):
        if not isinstance(id, int):
            raise Exception("Not support such type")

        return self.session.query(SiteConfig).filter_by(id=id).first()

    def get_sites(self):
        return self.session.query(SiteConfig).all()

    def delete_site(self, id):
        if not isinstance(id, int):
            raise Exception("Not support such type")

        site = self.session.query(SiteConfig).filter_by(id=id).first()
        if site is None:
            return SiteDeleteResponse(
                "Site with id = {0} not found".format(id),
                ResponseStatus.error
            )
        else:
            self.session.delete(site)
            self.session.commit()

            pykka.ActorRegistry.broadcast(SiteDeleteResponse(
                "Site was deleted",
                ResponseStatus.success,
                site.id
            ))

    def update_site(self, site):
        self.session.commit()
        pykka.ActorRegistry.broadcast(site)