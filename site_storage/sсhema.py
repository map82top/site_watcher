import enum
from sqlalchemy import Table, Column, Integer, String, Text, Enum, MetaData, DateTime, ForeignKey, create_engine
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()
engine = create_engine('sqlite:///foo.db', echo=False, connect_args={'check_same_thread': False})


class WatchStatus(str, enum.Enum):
    NEW = 'NEW'
    IN_PROGRESS = 'IN_PROGRESS'
    WATCHED = 'WATCHED'
    NEED_TO_WATCH = 'NEED_TO_WATCH'
    ERROR = 'ERROR'


class RegularCheck(str, enum.Enum):
    TWICE_HOUR = 'TWICE_HOUR'
    ONCE_HOUR = 'ONCE_HOUR'
    FOUR_TIMES_DAY = 'FOUR_TIMES_DAY'
    TWICE_DAY = 'TWICE_DAY'
    ONCE_DAY = 'ONCE_DAY'


Base = declarative_base(metadata)


class Site(Base):
    __tablename__ = 'sites'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    url = Column(String(100))
    status = Column(Enum(WatchStatus), default=WatchStatus.NEW)
    regular_check = Column(Enum(RegularCheck))
    last_watch = Column(DateTime, nullable=True)
    count_watches = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    keys = Column(Text, default='[]')

    def __init__(self, name, url, regular_check, keys='[]'):
        self.name = name
        self.url = url
        self.regular_check = regular_check
        self.keys = keys

class SiteVersion(Base):
    __tablename__ = 'site_version'
    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey(Site.id))
    content = Column(Text)
    differences = Column(Text)
    match_keys = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    count_changes = Column(Integer)
    count_match_keys = Column(Integer)

    def __init__(self, site_id, content, differences, match_keys, count_changes, count_match_keys):
        self.site_id = site_id
        self.content = content
        self.differences = differences
        self.match_keys = match_keys
        self.count_changes = count_changes
        self.count_match_keys = count_match_keys

Base.metadata.create_all(engine)