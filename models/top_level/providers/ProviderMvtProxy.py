from dataclasses import dataclass, field

from .records import ProviderTypes
from ..providers import ProviderTemplate
from ..utils import is_valid_string
from ...utils import update_dataclass_from_dict


@dataclass(kw_only=True)
class MvtProxyZoom:
    min: int | None = None
    max: int | None = None


@dataclass(kw_only=True)
class MvtProxyOptions:
    zoom: MvtProxyZoom | None = None
    # not implemented (greyed out in the UI)
    schemes: list | None = None


@dataclass(kw_only=True)
class MvtProxyFormat:
    name: str = ""
    mimetype: str = ""


# All Provider subclasses need to have default values even for mandatory fields,
# so that the empty instance can be created and filled with values later
@dataclass(kw_only=True)
class ProviderMvtProxy(ProviderTemplate):

    # overwriting default values of the parent class
    type: ProviderTypes = ProviderTypes.TILE
    name: str = "MVT-proxy"
    data: str = ""

    # provider-specific attributes
    options: MvtProxyOptions | None = None
    format: MvtProxyFormat = field(default_factory=lambda: MvtProxyFormat())

    def assign_ui_dict_to_provider_data_on_save(
        self, values: dict[str, str | list | int]
    ):

        # adjust structure to match the class structure
        values["options"] = {}
        values["format"] = {}

        # custom change
        values["options"]["zoom"] = {}
        values["options"]["zoom"]["min"] = values["options.zoom.min"]
        values["options"]["zoom"]["max"] = values["options.zoom.max"]
        values["options"]["schemes"] = values["options.schemes"]

        values["format"]["name"] = values["format.name"]
        values["format"]["mimetype"] = values["format.mimetype"]

        update_dataclass_from_dict(self, values, "ProviderMvtProxy")

        # Exception: if Zoom values are empty (e.g. missing in the UI), they will not overwrite the class attributes
        # This happens because if new value is abcent, there is nothing we can replace a default 'int' with. Manual overwrite:
        if values["options.zoom.min"] is None and values["options.zoom.max"] is None:
            self.options.zoom = None

    @classmethod
    def ui_elements_grid(cls):
        # Mandatory to align the fields order with data packing and assigning.
        # label, data_type, default, special_widget_type, placeholder
        return [
            (*cls.get_field_info(cls, "name*"), "QComboBox", ["MVT-proxy"]),
            (*cls.get_field_info(cls, "data*"), None, ""),
            (*cls.get_field_info(cls, "format.name*"), None, ""),
            (*cls.get_field_info(cls, "format.mimetype*"), None, ""),
            # non-mandatory
            (*cls.get_field_info(cls, "crs"), None, ""),
            (*cls.get_field_info(cls, "options.zoom.min"), None, ""),
            (*cls.get_field_info(cls, "options.zoom.max"), None, ""),
            (*cls.get_field_info(cls, "options.schemes"), "disabled", ""),
        ]

    def pack_data_to_list(self):
        return [
            self.type.value,
            self.name,
            self.data,
            self.format.name,
            self.format.mimetype,
            # non-mandatory
            self.crs,
            self.options.zoom.min if (self.options and self.options.zoom) else None,
            self.options.zoom.max if (self.options and self.options.zoom) else None,
            self.options.schemes if self.options else None,
        ]

    def assign_value_list_to_provider_data_on_read(self, values: list):
        if len(values) != 9:
            raise ValueError(
                f"Unexpected number of value to unpack: {len(values)}. Expected: 9"
            )

        self.name: str = values[1]
        self.data: str = values[2]
        self.format.name: str = values[3]
        self.format.mimetype: str = values[4]

        # non-mandatory
        self.crs: list | None = (
            values[5].split(",") if is_valid_string(values[5]) else None
        )

        # implement Options only if one of the child values provided

        try:
            options_zoom_min: int = int(values[6])
        except ValueError:
            options_zoom_min = None
        try:
            options_zoom_max: int = int(values[7])
        except ValueError:
            options_zoom_max = None

        options_schemes: list | None = (
            values[8].split(",") if is_valid_string(values[8]) else None
        )
        if options_zoom_min or options_zoom_max or options_schemes:
            self.options = MvtProxyOptions()
            self.options.schemes = options_schemes
            if options_zoom_min is not None or options_zoom_max is not None:
                self.options.zoom = MvtProxyZoom()
                self.options.zoom.min = options_zoom_min
                self.options.zoom.max = options_zoom_max

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

        return all_invalid_fields
