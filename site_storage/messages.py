import enum
from dataclasses import dataclass
from .sсhema import RegularCheck, WatchStatus
import datetime
from pykka import ActorRef


class ResponseStatus(str, enum.Enum):
    error = 'error'
    info = 'info'
    success = 'success'


@dataclass
class SiteDeleteRequest:
   id: int


@dataclass
class SiteDeleteResponse:
    message: str
    status: ResponseStatus
    id: int = None

@dataclass
class SiteUpdateResponse:
    message: str
    status: ResponseStatus


@dataclass
class SiteCreateResponse:
    message: str
    status: ResponseStatus


@dataclass
class CreateSiteRequest:
        name: str
        url: str
        keys: list
        selectors: list
        regular_check: RegularCheck


@dataclass
class SiteResponse:
        id: id
        name: str
        url: str
        keys: list
        selectors: list
        last_watch: datetime = None
        count_watches: int = 0
        regular_check: RegularCheck = RegularCheck.ONCE_DAY
        status: WatchStatus = WatchStatus.NEW
        created_at: datetime = None

@dataclass
class UpdateSiteRequest:
        id: int
        name: str = None
        url: str = None
        keys: list = None
        selectors: list = None
        last_watch: datetime = None
        count_watches: int = None
        regular_check: RegularCheck = None
        status: WatchStatus = None
        created_at: datetime = None


@dataclass
class SubscribeOnSiteUpdates:
        actor_proxy: ActorRef


@dataclass
class SubscribeOnVersionsUpdates:
        actor_proxy: ActorRef


@dataclass
class SaveSiteVersion:
    site_id: int
    content: str
    differences: str
    match_keys: str
    count_changes: int
    count_match_keys: int


@dataclass
class SiteVersionResponse:
    id: int
    site_id: int
    content: str
    differences: str
    match_keys: str
    count_changes: int
    count_match_keys: int
    created_at: datetime