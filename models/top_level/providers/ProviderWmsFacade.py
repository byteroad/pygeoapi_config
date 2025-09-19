from dataclasses import dataclass, field

from .records import ProviderTypes
from ..providers import ProviderTemplate
from ..utils import is_valid_string
from ...utils import update_dataclass_from_dict


@dataclass(kw_only=True)
class WmsFacadeOptions:
    layer: str = ""
    version: str | None = None
    style: str | None = None


@dataclass(kw_only=True)
class WmsFacadeFormat:
    name: str | None = None
    mimetype: str | None = None


# All Provider subclasses need to have default values even for mandatory fields,
# so that the empty instance can be created and filled with values later
@dataclass(kw_only=True)
class ProviderWmsFacade(ProviderTemplate):

    # overwriting default values of the parent class
    type: ProviderTypes = ProviderTypes.MAP
    name: str = "WMSFacade"
    data: str = ""

    # provider-specific attributes
    options: WmsFacadeOptions = field(default_factory=lambda: WmsFacadeOptions())
    format: WmsFacadeFormat | None = None

    def assign_ui_dict_to_provider_data(self, values: dict[str, str | list | int]):

        # adjust structure to match the class structure
        values["options"] = {}
        values["format"] = {}

        # custom change
        values["options"]["layer"] = values["options.layer"]
        values["options"]["style"] = values["options.style"]
        values["options"]["version"] = values["options.version"]

        values["format"]["name"] = values["format.name"]
        values["format"]["mimetype"] = values["format.mimetype"]

        update_dataclass_from_dict(self, values, "ProviderWmsFacade")

    def pack_data_to_list(self):
        return [
            self.type.value,
            self.name,
            self.crs,
            self.data,
            self.options.layer,
            self.options.style,
            self.options.version,
            self.format.name,
            self.format.mimetype,
        ]

    def assign_value_list_to_provider_data(self, values: list):
        if len(values) != 9:
            raise ValueError(
                f"Unexpected number of value to unpack: {len(values)}. Expected: 9"
            )

        self.name = values[1]
        self.crs = values[2].split(",") if is_valid_string(values[2]) else None
        self.data = values[3]
        self.options.layer = values[4]
        self.options.style = values[5]
        self.options.version = values[6]

        format_name = values[7] if is_valid_string(values[7]) else None
        format_mimetype = values[8] if is_valid_string(values[8]) else None
        if format_name or format_mimetype:
            self.format = WmsFacadeFormat()
            self.format.name = format_name
            self.format.mimetype = format_mimetype

    def get_invalid_properties(self):
        """Checks the values of mandatory fields."""
        all_invalid_fields = []

        if not isinstance(self.type, ProviderTypes):
            all_invalid_fields.append("type")
        if not is_valid_string(self.name):
            all_invalid_fields.append("name")
        if not is_valid_string(self.data):
            all_invalid_fields.append("data")
        if not is_valid_string(self.format.name):
            all_invalid_fields.append("format.name")
        if not is_valid_string(self.format.mimetype):
            all_invalid_fields.append("format.mimetype")
        if not is_valid_string(self.options.layer):
            all_invalid_fields.append("options.layer")
        if not is_valid_string(self.options.style):
            all_invalid_fields.append("options.style")
        if not is_valid_string(self.options.version):
            all_invalid_fields.append("options.version")

        return all_invalid_fields
