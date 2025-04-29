# Copyright (c) 2025, JACQUES Chan Alex and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.core.doctype.data_import.importer import ImportFile
from eval_app.data_management.doctype.import_csv.csv_importer import CsvImporter


class ImportCsv(Document):
	def start_import(self):
		if (self.ref_doctype):
			return False
		return True

	def get_importer(self,file_path):
		return CsvImporter(self.ref_doctype,file_path,self)
	
	@frappe.whitelist()
	def get_html_preview(self , import_file):
		if import_file:
			self.file = import_file
		i = self.get_importer(import_file)
		return 



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

