from abc import ABC, abstractmethod
from dataclasses import dataclass, is_dataclass, MISSING
from typing import Any, Type, get_type_hints
from .records import ProviderTypes


# this class doesn't need to be initialized on its own, only the subclasses
# All Provider subclasses need to have default values even for mandatory fields,
# so that the empty instance can be created and filled with values later
@dataclass(kw_only=True)
class ProviderTemplate(ABC):
    """Class to represent a Provider configuration template."""

    type: ProviderTypes
    name: str
    data: Any

    # optional, but with assumed default value:
    crs: list | None = None

    @abstractmethod
    def ui_elements_grid(cls):
        """Return specifications for the UI dialog for the given Resource Provider.
        Each UI element is reading from the assigned type and default value of class property.
        """
        return []

    def get_field_info(cls: Type, field_path: str) -> tuple[str, Type, Any]:
        """
        Inspect a (possibly nested) dataclass field on `cls` and return (type, default_value).
        If no default is defined, default_value is None.
        """
        parts = field_path.split(".")
        current_cls = cls
        default = None
        field_type = None

        for i, part in enumerate(parts):
            type_hints = get_type_hints(current_cls)
            field_type = type_hints.get(part)
            field_obj = current_cls.__dataclass_fields__[part]

            # Get default or default_factory
            default = field_obj.default
            if default is MISSING:
                factory = field_obj.default_factory
                if factory is not MISSING:
                    default = factory()
                else:
                    default = None

            # If there are more nested parts, move deeper
            if i < len(parts) - 1:
                # If default is None but field_type is a dataclass, instantiate a dummy
                if default is None and is_dataclass(field_type):
                    default = field_type()
                current_cls = field_type

        return field_path, field_type, default

    @staticmethod
    def init_provider_from_type(provider_type: ProviderTypes):
        """Return empty instance of the subclass, based on the requested type.
        Imports are inside the method to avoid circular imports from subclasses."""
        from . import ProviderPostgresql, ProviderWmsFacade, ProviderMvtProxy

        if provider_type == ProviderTypes.FEATURE:
            return ProviderPostgresql()

        elif provider_type == ProviderTypes.MAP:
            return ProviderWmsFacade()

        elif provider_type == ProviderTypes.TILE:
            return ProviderMvtProxy()

    @abstractmethod
    def assign_ui_dict_to_provider_data(self, values: dict[str, str | list | int]):
        """Takes the dictionary of values specific to provider type, and assigns them to the class instance."""
        pass

    @abstractmethod
    def assign_value_list_to_provider_data(self):
        """Takes a list of values specific to provider type, and assigns them to the class instance."""
        pass

    @abstractmethod
    def pack_data_to_list(self) -> list:
        """Returns a list with all instance properties in a specific order."""
        pass
