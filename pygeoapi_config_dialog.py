# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PygeoapiConfigDialog
                                 A QGIS plugin
 Update pygeoapi configuration file
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2025-05-16
        git sha              : $Format:%H$
        copyright            : (C) 2025 by ByteRoad
        email                : info@byteroad.net
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import yaml

from qgis.PyQt import uic
from qgis.core import QgsMessageLog
from qgis.PyQt import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDialogButtonBox  # or PyQt6.QtWidgets
from PyQt5.QtCore import QFile, QTextStream  # Not strictly needed, can use Python file API instead


# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'pygeoapi_config_dialog_base.ui'))


class PygeoapiConfigDialog(QtWidgets.QDialog, FORM_CLASS):


    yaml_str = ""

    def __init__(self, parent=None):
        """Constructor."""
        super(PygeoapiConfigDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)



    def on_button_clicked(self, button):
        role = self.buttonBox.buttonRole(button)
        print(f"Button clicked: {button.text()}, Role: {role}")

        # You can also check the standard button type
        if button == self.buttonBox.button(QDialogButtonBox.Save):
            self.save_to_file()
        elif button == self.buttonBox.button(QDialogButtonBox.Open):
            self.open_file()
        elif button == self.buttonBox.button(QDialogButtonBox.Close):
            self.reject()


    def write_yaml(self):

        try:

            # bind
            self.yaml_str['server']['bind']['host'] = self.lineEditHost.text()
            self.yaml_str['server']['bind']['port'] = self.spinBoxPort.value()

            # gzip
            self.yaml_str['server']['gzip'] = self.checkBoxGzip.isChecked()

            # pretty print
            self.yaml_str['server']['pretty_print'] = self.checkBoxPretty.isChecked()
            
            # admin
            self.yaml_str['server']['admin']=self.checkBoxAdmin.isChecked()

            # cors
            self.yaml_str['server']['cors']=self.checkBoxCors.isChecked()

            # map
            self.yaml_str['server']['map']['url'] = self.lineEditMapUrl.text()
            self.yaml_str['server']['map']['attribution'] = self.lineEditAttribution.text()

            # url
            self.yaml_str['server']['url'] = self.lineEditUrl.text()

            # language
            self.yaml_str['server']['languages']=[]
            for i in range(self.listWidgetLang.count()):
                item = self.listWidgetLang.item(i)
                if item.isSelected():
                    self.yaml_str['server']['languages'].append(item.text())

            # limits
            self.yaml_str['server']['limits']['default_items'] = self.spinBoxDefault.value()
            self.yaml_str['server']['limits']['max_items'] = self.spinBoxMax.value()

            self.yaml_str['server']['limits']['on_exceed'] = self.comboBoxExceed.currentText()

        except Exception as e:
            QgsMessageLog.logMessage(f"Error deserializing: {e}")

    def save_to_file(self):

        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "YAML Files (*.yml);;All Files (*)")

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    self.write_yaml()
                    yaml.dump(self.yaml_str, file)
                QgsMessageLog.logMessage(f"File saved to: {file_path}")
            except Exception as e:
                QgsMessageLog.logMessage(f"Error saving file: {e}")

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "YAML Files (*.yml);;All Files (*)")
        
        if not file_name:
            return

        try:
            with open(file_name, 'r', encoding='utf-8') as file:
                file_content = file.read()
                self.yaml_str = yaml.safe_load(file_content)

                self.read_yaml(self.yaml_str)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Cannot open file:\n{str(e)}")


    def select_items_by_text(list_widget, texts_to_select):
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            if item.text() in texts_to_select:
                item.setSelected(True)

    def read_yaml(self, text):

        # bind
        self.lineEditHost.setText(text['server']['bind']['host'])
        self.spinBoxPort.setValue(text['server']['bind']['port'])

        # gzip
        self.checkBoxGzip.setChecked(text['server']['gzip'])

        # pretty print
        self.checkBoxPretty.setChecked(text['server']['pretty_print'])

        # admin
        self.checkBoxAdmin.setChecked(text['server']['admin'])

        # cors
        self.checkBoxCors.setChecked(text['server']['cors'])

        # map
        self.lineEditMapUrl.setText(text['server']['map']['url'])
        self.lineEditAttribution.setText(text['server']['map']['attribution'])

        self.lineEditUrl.setText(text['server']['url'])

        # language
        for i in range(self.listWidgetLang.count()):
            item = self.listWidgetLang.item(i)
            if item.text() in text['server']['languages']:
                item.setSelected(True)

        # limits
        self.spinBoxDefault.setValue(text['server']['limits']['default_items'])
        self.spinBoxMax.setValue(text['server']['limits']['max_items'])

        for i in range(self.comboBoxExceed.count()):
            if self.comboBoxExceed.itemText(i) == text['server']['limits']['on_exceed']:
                self.comboBoxExceed.setCurrentText(text['server']['limits']['on_exceed'])
                break
