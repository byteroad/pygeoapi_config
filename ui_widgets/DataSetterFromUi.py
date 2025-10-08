from __future__ import annotations
import json
from typing import TYPE_CHECKING

from datetime import datetime

from .utils import get_widget_text_value

from .data_from_ui_setter_utils import (
    unpack_locales_values_list_to_dict,
    unpack_listwidget_values_to_sublists,
)
from ..models.top_level.utils import bbox_from_list

from ..models.top_level import (
    ResourceLinkTemplate,
    ResourceTemporalConfig,
    ResourceTypesEnum,
    ResourceVisibilityEnum,
    LoggingLevel,
    MetadataKeywordTypeEnum,
    MetadataRoleEnum,
    ServerOnExceedEnum,
    ServerOptionalBoolsEnum,
    ServerTemplatesConfig,
    ServerLimitsConfig,
)
from ..models.top_level.providers import ProviderTemplate
from ..models.top_level.providers.records import (
    Languages,
    ProviderTypes,
    TrsAuthorities,
)

from ..models.top_level.utils import (
    InlineList,
    get_enum_value_from_string,
    is_valid_string,
)


if TYPE_CHECKING:
    # preserve type checking, but don't import in runtime to avoid circular import
    from ..pygeoapi_config_dialog import PygeoapiConfigDialog
    from ..models.ConfigData import ConfigData


class DataSetterFromUi:

    dialog: PygeoapiConfigDialog

    def __init__(self, dialog: PygeoapiConfigDialog):
        self.dialog = dialog

    def set_data_from_ui(self):
        """Collect all data from the main UI tabs and save to ConfigData."""
        dialog: PygeoapiConfigDialog = self.dialog
        config_data: ConfigData = dialog.config_data

        # bind
        config_data.server.bind.host = dialog.lineEditHost.text()
        try:
            config_data.server.bind.port = int(dialog.lineEditPort.text())
        except ValueError:
            config_data.server.bind.port = dialog.lineEditPort.text()

        # gzip
        config_data.server.gzip = get_enum_value_from_string(
            ServerOptionalBoolsEnum, dialog.comboBoxGzip.currentText()
        )

        # pretty print
        config_data.server.pretty_print = get_enum_value_from_string(
            ServerOptionalBoolsEnum, dialog.comboBoxPretty.currentText()
        )

        # admin
        config_data.server.admin = get_enum_value_from_string(
            ServerOptionalBoolsEnum, dialog.comboBoxAdmin.currentText()
        )

        # cors
        config_data.server.cors = get_enum_value_from_string(
            ServerOptionalBoolsEnum, dialog.comboBoxCors.currentText()
        )

        # templates
        if is_valid_string(dialog.lineEditTemplatesPath.text()) or is_valid_string(
            dialog.lineEditTemplatesStatic.text()
        ):
            config_data.server.templates = ServerTemplatesConfig()
        else:
            config_data.server.templates = None

        if config_data.server.templates:
            config_data.server.templates.path = dialog.lineEditTemplatesPath.text()
            config_data.server.templates.static = dialog.lineEditTemplatesStatic.text()

        # map
        config_data.server.map.url = dialog.lineEditMapUrl.text()
        config_data.server.map.attribution = dialog.lineEditAttribution.text()

        # url
        config_data.server.url = dialog.lineEditUrl.text()

        # language single
        config_data.server.language = get_enum_value_from_string(
            Languages, dialog.comboBoxLangSingle.currentText()
        )

        # languages
        config_data.server.languages = []
        languages_lists = unpack_listwidget_values_to_sublists(
            dialog.listWidgetServerLangs
        )
        for lang in languages_lists:
            if is_valid_string(lang[0]):
                config_data.server.languages.append(lang[0])

        # limits
        default_items = dialog.spinBoxDefault.value()
        max_items = dialog.spinBoxMax.value()

        on_exceed = get_enum_value_from_string(
            ServerOnExceedEnum, dialog.comboBoxExceed.currentText()
        )
        if default_items or max_items or on_exceed:
            config_data.server.limits = ServerLimitsConfig()
            config_data.server.limits.default_items = default_items
            config_data.server.limits.max_items = max_items
            config_data.server.limits.on_exceed = on_exceed

        # logging
        config_data.logging.level = get_enum_value_from_string(
            LoggingLevel, dialog.comboBoxLog.currentText()
        )

        if is_valid_string(dialog.lineEditLogfile.text()):
            config_data.logging.logfile = dialog.lineEditLogfile.text()
        else:
            config_data.logging.logfile = None

        if is_valid_string(dialog.lineEditLogformat.text()):
            config_data.logging.logformat = dialog.lineEditLogformat.text()
        else:
            config_data.logging.logformat = None

        if is_valid_string(dialog.lineEditDateformat.text()):
            config_data.logging.dateformat = dialog.lineEditDateformat.text()
        else:
            config_data.logging.dateformat = None

        # metadata identification
        config_data.metadata.identification.title = unpack_locales_values_list_to_dict(
            dialog.listWidgetMetadataIdTitle, False
        )
        config_data.metadata.identification.description = (
            unpack_locales_values_list_to_dict(
                dialog.listWidgetMetadataIdDescription, False
            )
        )
        config_data.metadata.identification.keywords = (
            unpack_locales_values_list_to_dict(
                dialog.listWidgetMetadataIdKeywords, True
            )
        )

        keywords_type = get_enum_value_from_string(
            MetadataKeywordTypeEnum, dialog.comboBoxMetadataIdKeywordsType.currentText()
        )
        config_data.metadata.identification.keywords_type = (
            keywords_type if is_valid_string(keywords_type) else None
        )

        config_data.metadata.identification.terms_of_service = (
            self.valid_string_or_none(dialog.lineEditMetadataIdTerms)
        )
        config_data.metadata.identification.url = dialog.lineEditMetadataIdUrl.text()

        # metadata license
        config_data.metadata.license.name = dialog.lineEditMetadataLicenseName.text()
        config_data.metadata.license.url = self.valid_string_or_none(
            dialog.lineEditMetadataLicenseUrl
        )

        # metadata provider
        config_data.metadata.provider.name = dialog.lineEditMetadataProviderName.text()
        config_data.metadata.provider.url = self.valid_string_or_none(
            dialog.lineEditMetadataProviderUrl
        )

        # metadata contact
        config_data.metadata.contact.name = dialog.lineEditMetadataContactName.text()
        config_data.metadata.contact.position = self.valid_string_or_none(
            dialog.lineEditMetadataContactPosition
        )
        config_data.metadata.contact.address = self.valid_string_or_none(
            dialog.lineEditMetadataContactAddress
        )
        config_data.metadata.contact.city = dialog.lineEditMetadataContactCity.text()
        config_data.metadata.contact.stateorprovince = self.valid_string_or_none(
            dialog.lineEditMetadataContactState
        )
        config_data.metadata.contact.postalcode = self.valid_string_or_none(
            dialog.lineEditMetadataContactPostal
        )
        config_data.metadata.contact.country = self.valid_string_or_none(
            dialog.lineEditMetadataContactCountry
        )
        config_data.metadata.contact.phone = self.valid_string_or_none(
            dialog.lineEditMetadataContactPhone
        )
        config_data.metadata.contact.fax = self.valid_string_or_none(
            dialog.lineEditMetadataContactFax
        )
        config_data.metadata.contact.email = self.valid_string_or_none(
            dialog.lineEditMetadataContactEmail
        )
        config_data.metadata.contact.url = self.valid_string_or_none(
            dialog.lineEditMetadataContactUrl
        )
        config_data.metadata.contact.hours = self.valid_string_or_none(
            dialog.lineEditMetadataContactHours
        )
        config_data.metadata.contact.instructions = self.valid_string_or_none(
            dialog.lineEditMetadataContactInstructions
        )
        role = get_enum_value_from_string(
            MetadataRoleEnum,
            dialog.comboBoxMetadataContactRole.currentText(),
        )
        config_data.metadata.contact.role = role if is_valid_string(role) else None

    def valid_string_or_none(self, line_edit):
        text_value = line_edit.text()
        return text_value if is_valid_string(text_value) else None

    def set_resource_data_from_ui(self):
        """Collect data from Resource UI and add to ConfigData."""
        dialog: PygeoapiConfigDialog = self.dialog
        config_data: ConfigData = dialog.config_data
        res_name = dialog.current_res_name

        config_data.resources[res_name].type = get_enum_value_from_string(
            ResourceTypesEnum, dialog.comboBoxResType.currentText()
        )
        config_data.resources[res_name].title = unpack_locales_values_list_to_dict(
            dialog.listWidgetResTitle, False
        )
        config_data.resources[res_name].description = (
            unpack_locales_values_list_to_dict(dialog.listWidgetResDescription, False)
        )
        config_data.resources[res_name].keywords = unpack_locales_values_list_to_dict(
            dialog.listWidgetResKeywords, True
        )

        # visibility: if empty, ignore
        if is_valid_string(dialog.comboBoxResVisibility.currentText()):
            config_data.resources[res_name].visibility = get_enum_value_from_string(
                ResourceVisibilityEnum, dialog.comboBoxResVisibility.currentText()
            )
        else:
            config_data.resources[res_name].visibility = None

        # spatial bbox
        raw_bbox_list = [
            get_widget_text_value(x)
            for x in [
                dialog.lineEditResExtentsSpatialXMin,
                dialog.lineEditResExtentsSpatialYMin,
                dialog.lineEditResExtentsSpatialXMax,
                dialog.lineEditResExtentsSpatialYMax,
            ]
        ]
        # this loop is to not add empty decimals to int unnecessarily
        config_data.resources[res_name].extents.spatial.bbox = InlineList(
            bbox_from_list(raw_bbox_list)
        )

        # spatial crs
        config_data.resources[res_name].extents.spatial.crs = (
            self.get_extents_crs_from_ui(dialog)
            if is_valid_string(dialog.lineEditResExtentsSpatialCrs)
            else None
        )

        # temporal: only initialize if any of the values are present, otherwise leave as default None
        # IGNORE trs if no other values are present
        temporal_begin = None
        temporal_end = None
        if is_valid_string(dialog.lineEditResExtentsTemporalBegin.text()):
            temporal_begin = datetime.strptime(
                dialog.lineEditResExtentsTemporalBegin.text(),
                "%Y-%m-%dT%H:%M:%SZ",
            )
        if is_valid_string(dialog.lineEditResExtentsTemporalEnd.text()):
            temporal_end = datetime.strptime(
                dialog.lineEditResExtentsTemporalEnd.text(),
                "%Y-%m-%dT%H:%M:%SZ",
            )

        if temporal_begin or temporal_end:
            config_data.resources[res_name].extents.temporal = ResourceTemporalConfig()

            config_data.resources[res_name].extents.temporal.begin = temporal_begin
            config_data.resources[res_name].extents.temporal.end = temporal_end
            config_data.resources[res_name].extents.temporal.trs = (
                get_enum_value_from_string(
                    TrsAuthorities,
                    get_widget_text_value(dialog.comboBoxResExtentsTemporalTrs),
                )
            )

        # links
        config_data.resources[res_name].links = []
        links_data_lists = unpack_listwidget_values_to_sublists(
            dialog.listWidgetResLinks, 6
        )
        for link in links_data_lists:
            new_link = ResourceLinkTemplate()
            new_link.type = link[0]
            new_link.rel = link[1]
            new_link.href = link[2]

            if is_valid_string(link[3]):
                new_link.title = link[3]
            if is_valid_string(link[4]):
                new_link.hreflang = link[4]
            if is_valid_string(link[5]):
                new_link.length = int(link[5])

            config_data.resources[res_name].links.append(new_link)

        # linked-data
        read_only_linked_data_lists: list[list[str]] = (
            unpack_listwidget_values_to_sublists(dialog.listWidgetResLinkedData, 1)
        )
        if len(read_only_linked_data_lists) > 0:
            new_linked_data = read_only_linked_data_lists[0][0]
            config_data.resources[res_name].linked__data = json.loads(new_linked_data)

        # providers
        config_data.resources[res_name].providers = []

        # add editable providers from a widget
        providers_data_lists: list[list[str]] = unpack_listwidget_values_to_sublists(
            dialog.listWidgetResProvider
        )

        for pr in providers_data_lists:
            provider_type = get_enum_value_from_string(ProviderTypes, pr[0])
            new_pr = ProviderTemplate.init_provider_from_type(provider_type)
            new_pr.assign_value_list_to_provider_data_on_read(pr)

            config_data.resources[res_name].providers.append(new_pr)

        # add read-only providers from another widget
        read_only_providers_data_lists: list[list[str]] = (
            unpack_listwidget_values_to_sublists(
                dialog.listWidgetResReadOnlyProviders, 1
            )
        )
        for read_pr in read_only_providers_data_lists:
            new_read_pr = read_pr[0]
            config_data.resources[res_name].providers.append(json.loads(new_read_pr))

        # change resource key to a new alias
        new_alias = dialog.lineEditResAlias.text()
        if res_name in config_data.resources:
            config_data.resources[new_alias] = config_data.resources.pop(res_name)

    def delete_selected_provider_type_and_name(self, list_widget):
        """Find and remove first matching resource provider with specified type and name."""
        dialog: PygeoapiConfigDialog = self.dialog
        config_data: ConfigData = dialog.config_data
        res_name = dialog.current_res_name

        # get selected provider data from a widget (by selection index)
        providers_data_lists: list[list] = unpack_listwidget_values_to_sublists(
            list_widget
        )
        selected_index = list_widget.currentRow()
        if selected_index < 0:
            return
        selected_pr_data = providers_data_lists[selected_index]
        selected_pr_type = get_enum_value_from_string(
            ProviderTypes, selected_pr_data[0]
        )
        selected_pr_name = selected_pr_data[1]

        # iterate through resource providers and delete the first matching one
        for res_provider in config_data.resources[res_name].providers:
            if isinstance(res_provider, dict):
                continue  # ignore read-only providers

            if (
                res_provider.name == selected_pr_name
                and res_provider.type == selected_pr_type
            ):
                config_data.resources[res_name].providers.remove(res_provider)
                break

    def get_extents_crs_from_ui(self, dialog):
        return (
            "http://www.opengis.net/def/crs/"
            + get_widget_text_value(dialog.comboBoxResExtentsSpatialCrsType)
            + "/"
            + get_widget_text_value(dialog.lineEditResExtentsSpatialCrs)
        )

    def get_invalid_resource_ui_fields(self) -> list[str]:
        """Get list of invalid UI values in Resource UI."""

        dialog: PygeoapiConfigDialog = self.dialog
        invalid_fields = []

        if not is_valid_string(dialog.lineEditResAlias.text()):
            invalid_fields.append("alias")
        if dialog.listWidgetResTitle.count() == 0:
            invalid_fields.append("title")
        if dialog.listWidgetResDescription.count() == 0:
            invalid_fields.append("description")
        if dialog.listWidgetResKeywords.count() == 0:
            invalid_fields.append("keywords")

        try:
            raw_bbox_list = [
                get_widget_text_value(x)
                for x in [
                    dialog.lineEditResExtentsSpatialXMin,
                    dialog.lineEditResExtentsSpatialYMin,
                    dialog.lineEditResExtentsSpatialXMax,
                    dialog.lineEditResExtentsSpatialYMax,
                ]
            ]
            bbox_from_list(raw_bbox_list)
        except:
            invalid_fields.append("spatial extents (bbox)")

        if (
            dialog.listWidgetResProvider.count() == 0
            and dialog.listWidgetResReadOnlyProviders.count() == 0
        ):
            invalid_fields.append("providers")

        # optional fields, but can cause crash if wrong format, so we need to warn about them already here
        if is_valid_string(dialog.lineEditResExtentsTemporalBegin.text()):
            try:
                datetime.strptime(
                    dialog.lineEditResExtentsTemporalBegin.text(), "%Y-%m-%dT%H:%M:%SZ"
                )
            except:
                invalid_fields.append("temporal extents (begin)")

        if is_valid_string(dialog.lineEditResExtentsTemporalEnd.text()):
            try:
                datetime.strptime(
                    dialog.lineEditResExtentsTemporalEnd.text(), "%Y-%m-%dT%H:%M:%SZ"
                )
            except:
                invalid_fields.append("temporal extents (end)")

        return invalid_fields
