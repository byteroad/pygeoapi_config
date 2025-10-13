from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlparse


# records
class MetadataKeywordTypeEnum(Enum):
    NONE = ""
    DISCIPLINE = "discipline"
    TEMPORAL = "temporal"
    PLACE = "place"
    THEME = "theme"
    STRATUM = "stratum"


class MetadataRoleEnum(Enum):
    NONE = ""
    AUTHOR = "author"
    COAUTHOR = "coAuthor"
    COLLABORATOR = "collaborator"
    CONTRIBUTOR = "contributor"
    CUSTODIAN = "custodian"
    DISTRIBUTOR = "distributor"
    EDITOR = "editor"
    FUNDER = "funder"
    MEDIATOR = "mediator"
    ORIGINATOR = "originator"
    OWNER = "owner"
    POINTOFCONTACT = "pointOfContact"
    PRINCIPALINVESTIGATOR = "principalInvestigator"
    PROCESSOR = "processor"
    PUBLISHER = "publisher"
    RESOURCEPROVIDER = "resourceProvider"
    RIGHTSHOLDER = "rightsHolder"
    SPONSOR = "sponsor"
    STAKEHOLDER = "stakeholder"
    USER = "user"


# data classes
@dataclass(kw_only=True)
class MetadataIdentificationConfig:
    title: str | dict = field(default_factory=lambda: "")
    description: str | dict = field(default_factory=lambda: "")
    keywords: list | dict = field(default_factory=lambda: [])
    url: str = field(default="https://example.org")
    keywords_type: MetadataKeywordTypeEnum | None = None
    terms_of_service: str | None = None


@dataclass(kw_only=True)
class MetadataLicenseConfig:
    name: str = field(default="CC-BY 4.0 license")
    url: str | None = None


@dataclass(kw_only=True)
class MetadataProviderConfig:
    name: str = field(default="Organization Name")
    url: str | None = None


@dataclass(kw_only=True)
class MetadataContactConfig:
    name: str = field(default="Lastname, Firstname")
    position: str | None = None
    address: str | None = None
    city: str | None = None
    stateorprovince: str | None = None
    postalcode: str | None = None
    country: str | None = None
    phone: str | None = None
    fax: str | None = None
    email: str | None = None
    url: str | None = None
    hours: str | None = None
    instructions: str | None = None
    role: MetadataRoleEnum | None = None


@dataclass(kw_only=True)
class MetadataConfig:
    """Placeholder class for Metadata configuration data."""

    identification: MetadataIdentificationConfig = field(
        default_factory=lambda: MetadataIdentificationConfig()
    )
    license: MetadataLicenseConfig = field(
        default_factory=lambda: MetadataLicenseConfig()
    )
    provider: MetadataProviderConfig = field(
        default_factory=lambda: MetadataProviderConfig()
    )
    contact: MetadataContactConfig = field(
        default_factory=lambda: MetadataContactConfig()
    )

    def get_invalid_properties(self):
        """Checks the values of mandatory fields: identification (title, description, keywords)."""
        all_invalid_fields = []

        if len(self.identification.title) == 0:
            all_invalid_fields.append("metadata.identification.title")
        if len(self.identification.description) == 0:
            all_invalid_fields.append("metadata.identification.description")
        if len(self.identification.keywords) == 0:
            all_invalid_fields.append("metadata.identification.keywords")
        if len(self.identification.url) == 0:
            all_invalid_fields.append("metadata.identification.url")
        if len(self.license.name) == 0:
            all_invalid_fields.append("metadata.license.name")
        if len(self.provider.name) == 0:
            all_invalid_fields.append("metadata.provider.name")
        if len(self.contact.name) == 0:
            all_invalid_fields.append("metadata.contact.name")

        # parsed_url = urlparse(self.identification.url)
        # if not all([parsed_url.scheme, parsed_url.netloc]):
        #    all_invalid_fields.append("metadata.identification.url")

        return all_invalid_fields
