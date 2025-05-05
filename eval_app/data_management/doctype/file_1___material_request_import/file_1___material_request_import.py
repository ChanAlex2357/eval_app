# Copyright (c) 2025, JACQUES Chan Alex and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from eval_app.data_management.doctype.file_1___material_request_import.file_1_data_importer import File1DataImporter

class File1MaterialRequestImport(Document):
	def get_data_stack_importer(self):
		return File1DataImporter()

	def import_data(self):
		pass
