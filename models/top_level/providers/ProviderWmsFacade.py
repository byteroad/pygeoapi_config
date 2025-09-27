from dataclasses import dataclass, field
from typing import get_type_hints

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

    @classmethod
    def ui_elements_grid(cls):
        # label, data_type, default, special_widget_type, placeholder
        return [
            (*cls.get_field_info(cls, "name"), str, "QComboBox", ["WMSFacade"]),
            (*cls.get_field_info(cls, "crs"), list, None, ""),
            (*cls.get_field_info(cls, "data"), str, None, ""),
            (*cls.get_field_info(cls, "options.layer"), str, None, ""),
            (*cls.get_field_info(cls, "options.style"), str, None, ""),
            (*cls.get_field_info(cls, "options.version"), str, None, ""),
            (*cls.get_field_info(cls, "format.name"), str, None, ""),
            (*cls.get_field_info(cls, "format.mimetype"), str, None, ""),
        ]

    def pack_data_to_list(self):
        return [
            self.type.value,
            self.name,
            self.data,
            self.options.layer,
            # non-mandatory
            self.crs,
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

        self.name: str = values[1]
        self.data: str = values[2]
        self.options.layer: str = values[3]

        # non-mandatory
        self.crs: list | None = (
            values[4].split(",") if is_valid_string(values[4]) else None
        )
        self.options.style: str | None = (
            values[5] if is_valid_string(values[5]) else None
        )
        self.options.version: str | None = (
            values[6] if is_valid_string(values[6]) else None
        )

        format_name: str | None = values[7] if is_valid_string(values[7]) else None
        format_mimetype: str | None = values[8] if is_valid_string(values[8]) else None
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
        if not is_valid_string(self.options.layer):
            all_invalid_fields.append("options.layer")

        return all_invalid_fields
