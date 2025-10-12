from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .providers import ProviderPostgresql, ProviderMvtProxy, ProviderWmsFacade
from .utils import (
    InlineList,
    bbox_from_list,
    get_enum_value_from_string,
    is_valid_string,
)
from .providers.records import CrsAuthorities


# records
class ResourceTypesEnum(Enum):
    COLLECTION = "collection"
    STAC = "stac-collection"


class ResourceVisibilityEnum(Enum):
    NONE = ""
    DEFAULT = "default"
    HIDDEN = "hidden"


# data classes
@dataclass(kw_only=True)
class ResourceLinkTemplate:
    """Class to represent a Link configuration template."""

    type: str = ""
    rel: str = ""
    href: str = ""

    # optional
    title: str | None = None
    hreflang: str | None = None
    length: int | None = None


@dataclass(kw_only=True)
class ResourceSpatialConfig:
    bbox: InlineList = field(default_factory=lambda: InlineList([-180, -90, 180, 90]))

    # optional
    crs: str | None = None

    # we need these as separate properties so that Enum class values can be set&selected in the UI
    @property
    def crs_authority(self):
        if self.crs is None:
            return CrsAuthorities.OGC13

        crs_auth_id = self.crs.split("http://www.opengis.net/def/crs/")[
            -1
        ]  # OGC/1.3/CRS84
        auth_string = "/".join(crs_auth_id.split("/")[:-1])
        try:
            return get_enum_value_from_string(CrsAuthorities, auth_string)
        except ValueError:
            # 'swallow' the error, as we technically accept any strings
            return CrsAuthorities.OGC13

    @property
    def crs_id(self):
        if self.crs is None:
            return ""
        return self.crs.split("/")[-1]


@dataclass(kw_only=True)
class ResourceTemporalConfig:

    # optional
    begin: datetime | None = None
    end: datetime | None = None
    trs: str | None = None


@dataclass(kw_only=True)
class ResourceExtentsConfig:
    """Class to represent Extents configuration template."""

    # fields with default values:
    spatial: ResourceSpatialConfig = field(
        default_factory=lambda: ResourceSpatialConfig()
    )

    # optional
    temporal: ResourceTemporalConfig | None = None


@dataclass(kw_only=True)
class ResourceConfigTemplate:
    """Class to represent a Resource configuration template."""

    # fields with default values:
    type: ResourceTypesEnum = field(
        default_factory=lambda: ResourceTypesEnum.COLLECTION
    )
    title: str | dict = field(default="")
    description: str | dict = field(default="")
    keywords: list | dict = field(default_factory=lambda: [])
    extents: ResourceExtentsConfig = field(
        default_factory=lambda: ResourceExtentsConfig()
    )
    # for providers, the types have to be explicitly listed so they are picked up on deserialization
    providers: list[
        ProviderPostgresql | ProviderMvtProxy | ProviderWmsFacade | dict
    ] = field(default_factory=lambda: [])

    # optional
    links: list[ResourceLinkTemplate] | None = None
    visibility: ResourceVisibilityEnum | None = None
    linked__data: dict | None = (
        None  # intentionally with double undersore to not confuse with any reserved keyword
    )
    # limits: ignored for now

    # Overwriding __init__ method to pass 'instance_name' as an input but not make it an instance property
    # This will allow to have a clean 'asdict(class)' output without 'instance_name' in it
    @classmethod
    def init_with_name(cls, *, instance_name: str):
        obj = cls()
        obj._instance_name = instance_name
        return obj

    @property
    def instance_name(self):
        return self._instance_name

    def validate_reassign_bbox(self) -> bool:
        """Validates the bbox values and converts to int/float if needed."""
        try:
            self.extents.spatial.bbox = bbox_from_list(self.extents.spatial.bbox)
            return True
        except ValueError:
            self.extents.spatial.bbox = InlineList([-180, -90, 180, 90])
            return False

    def get_invalid_properties(self):
        """Checks the values of mandatory fields: identification (title, description, keywords)."""
        all_invalid_fields = []

        if not isinstance(self.type, ResourceTypesEnum):
            all_invalid_fields.append("type")
        if len(self.title) == 0:
            all_invalid_fields.append("title")
        if len(self.description) == 0:
            all_invalid_fields.append("description")
        if len(self.keywords) == 0:
            all_invalid_fields.append("keywords")
        if len(self.providers) == 0:
            all_invalid_fields.append("providers")
        if len(self.extents.spatial.bbox) < 4 or len(self.extents.spatial.bbox) > 6:
            all_invalid_fields.append("extents.spatial.bbox")

        return all_invalid_fields
