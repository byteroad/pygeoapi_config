from dataclasses import dataclass, field
import json

from ...utils import update_dataclass_from_dict
from .records import ProviderTypes
from ..providers import ProviderTemplate
from ..utils import is_valid_string


@dataclass(kw_only=True)
class PostgresqlData:
    host: str = ""
    dbname: str = ""
    user: str = ""
    password: str | None = None
    port: int | str | None = None
    search_path: list | None = None  # field(default_factory=lambda: InlineList([]))


# All Provider subclasses need to have default values even for mandatory fields,
# so that the empty instance can be created and filled with values later
@dataclass(kw_only=True)
class ProviderPostgresql(ProviderTemplate):

    # overwriting default values of the parent class
    type: ProviderTypes = ProviderTypes.FEATURE
    name: str = "PostgreSQL"
    data: PostgresqlData = field(default_factory=lambda: PostgresqlData())

    # provider-specific attributes
    id_field: str = ""
    table: str = ""
    geom_field: str | None = None

    # optional
    storage_crs: str | None = None

    # not implemented by choice (greyed out in the UI)
    options: dict | None = None
    time_field: str | None = None
    properties: list | None = None

    def assign_ui_dict_to_provider_data_on_save(
        self, values: dict[str, str | list | int]
    ):
        # adjust structure to match the class structure
        values["data"] = {}
        for k, v in values.items():
            if k in [
                "data.host",
                "data.port",
                "data.dbname",
                "data.user",
                "data.password",
                "data.search_path",
            ]:
                values["data"][k.split(".")[1]] = v

        update_dataclass_from_dict(self, values, "ProviderPostgresql")

    @classmethod
    def ui_elements_grid(cls):
        # Mandatory to align the fields order with data packing and assigning.
        # label, data_type, default, special_widget_type, placeholder
        return [
            (*cls.get_field_info(cls, "name"), "QComboBox", ["PostgreSQL"]),
            (*cls.get_field_info(cls, "table"), None, ""),
            (*cls.get_field_info(cls, "id_field"), None, ""),
            (*cls.get_field_info(cls, "data.host"), None, ""),
            (
                *cls.get_field_info(cls, "data.dbname"),
                None,
                "",
            ),
            (*cls.get_field_info(cls, "data.user"), None, ""),
            # non-mandatory:
            (*cls.get_field_info(cls, "crs"), None, ""),
            (
                *cls.get_field_info(cls, "geom_field"),
                None,
                "",
            ),
            (
                *cls.get_field_info(cls, "storage_crs"),
                None,
                "e.g. http://www.opengis.net/def/crs/OGC/1.3/CRS84",
            ),
            (
                *cls.get_field_info(cls, "data.password"),
                None,
                "",
            ),
            (*cls.get_field_info(cls, "data.port"), None, ""),
            (
                *cls.get_field_info(cls, "data.search_path"),
                None,
                "e.g. 'osm, public'",
            ),
            # not implemented
            (*cls.get_field_info(cls, "options"), "disabled", ""),
            (
                *cls.get_field_info(cls, "time_field"),
                "disabled",
                "",
            ),
            (
                *cls.get_field_info(cls, "properties"),
                "disabled",
                "",
            ),
        ]

    def pack_data_to_list(self):
        return [
            self.type.value,
            self.name,
            self.table,
            self.id_field,
            self.data.host,
            self.data.dbname,
            self.data.user,
            # non-mandatory:
            self.crs,
            self.geom_field,
            self.storage_crs,
            self.data.password,
            self.data.port,
            self.data.search_path,
            # not implemented
            self.options,
            self.time_field,
            self.properties,
        ]

    def assign_value_list_to_provider_data_on_read(self, values: list):
        print("_______assign_value_list_to_provider_data_on_read")
        if len(values) != 16:
            raise ValueError(
                f"Unexpected number of value to unpack: {len(values)}. Expected: 16"
            )

        # self.type = get_enum_value_from_string(ProviderTypes, pr[0])

        self.name: str = values[1]
        self.table: str = values[2]
        self.id_field: str = values[3]

        self.data.host: str = values[4]
        self.data.dbname: str = values[5]
        self.data.user: str = values[6]

        # non-mandatory:
        self.crs: list | None = (
            values[7].split(",") if is_valid_string(values[7]) else None
        )
        self.geom_field: str | None = values[8] if is_valid_string(values[8]) else None
        self.storage_crs: str | None = (
            values[9] if is_valid_string(values[79]) else None
        )
        self.data.password: str | None = (
            values[10] if is_valid_string(values[10]) else None
        )
        try:
            self.data.port = int(values[11])
        except ValueError:
            self.data.port: str | None = (
                values[11] if is_valid_string(values[11]) else None
            )
        self.data.search_path: list | None = (
            values[12].split(",") if is_valid_string(values[12]) else []
        )
        self.options: dict | None = (
            json.loads(values[13]) if is_valid_string(values[13]) else None
        )
        self.time_field: str | None = (
            values[14] if is_valid_string(values[14]) else None
        )
        self.properties: list | None = (
            values[15].split(",") if is_valid_string(values[15]) else None
        )

    def get_invalid_properties(self):
        """Checks the values of mandatory fields."""
        all_invalid_fields = []

        if not isinstance(self.type, ProviderTypes):
            all_invalid_fields.append("type")
        if not is_valid_string(self.name):
            all_invalid_fields.append("name")

        if not is_valid_string(self.id_field):
            all_invalid_fields.append("id_field")
        if not is_valid_string(self.table):
            all_invalid_fields.append("table")

        if not is_valid_string(self.data.host):
            all_invalid_fields.append("data.host")
        if not is_valid_string(self.data.dbname):
            all_invalid_fields.append("data.dbname")
        if not is_valid_string(self.data.user):
            all_invalid_fields.append("data.user")

        return all_invalid_fields
