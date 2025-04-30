# Copyright (c) 2025, JACQUES Chan Alex and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.core.doctype.data_import.importer import ImportFile
from eval_app.data_management.doctype.import_csv.csv_importer import CsvImporter
import json


class ImportCsv(Document):
	def start_import(self):
		
		if not self.file:
			frappe.throw(_("Please upload a file to import."))

		if not self.ref_doctype:
			frappe.throw(_("Please select a reference doctype."))

		if not self.file.endswith(".csv"):
			frappe.throw(_("Only CSV files are supported."))

		self.importer = self.get_importer(self.file)
		self.importer.import_data()

		return True

	def get_importer(self,file_path):
		return CsvImporter(self.ref_doctype,file_path,self)
	
	@frappe.whitelist()
	def get_html_preview(self , import_file):
		if import_file:
			self.file = import_file
		i = self.get_importer(import_file)
		out = i.parse_file()
		import_logs = {}
		if self.import_logs:
			il = (self.import_logs)
			import_logs = json.loads(il)

		out['import_logs'] = (import_logs)
		return out



@frappe.whitelist()
def form_start_import(import_name: str):
	di: ImportCsv = frappe.get_doc("Import Csv", import_name)
	return di.start_import()

@frappe.whitelist()
def get_html_preview(
	import_name: str, import_file: str
):
	di: ImportCsv = frappe.get_doc("Import Csv", import_name)
	return di.get_html_preview(import_file)

