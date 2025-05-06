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
		
		import_logs, errors_count, success_count =  self.importer.import_data()
		result_status = 1
		if errors_count > 0:
			error_status = -1 if success_count == 0 else 0
			# frappe.db.set_value("Import Csv", self.name, "status", error_status)
			result_status = error_status
		
		return result_status , import_logs, errors_count, success_count

	def set_status(self, status, logs):
		status_str = ""
		if status == 1:
			status_str = "Success"
		elif status == 0:
			status_str = "Partial Success"
		else:
			status_str = "Error"
		try:
			frappe.db.set_value("Import Csv", self.name, "status", status_str)
			frappe.db.set_value("Import Csv", self.name, "import_logs", json.dumps(logs))
		except Exception as e:
			raise Exception("Erreur lors de la mise a jour du status de l'import : "+str(e))

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
			il_data = json.loads(il)
			import_logs = il_data

		out['import_logs'] = (import_logs)
		return out

@frappe.whitelist()
def form_start_import(import_name: str):
	di: ImportCsv = frappe.get_doc("Import Csv", import_name)
	import_status = "" 
	import_logs = [] 
	errors_count = 0
	success_count = 0
	try:
		frappe.db.begin()
		import_status, import_logs, errors_count, success_count = di.start_import()
		if import_status != 1:
			raise Exception(f"{errors_count} erreurs d'importation")
		frappe.db.commit()
	except Exception as e:
		frappe.db.rollback()
		raise e
	finally:
		di.set_status(import_status, import_logs)
		frappe.db.commit()
		frappe.db.close()
		
	return True

@frappe.whitelist()
def get_html_preview(
	import_name: str, import_file: str
):
	di: ImportCsv = frappe.get_doc("Import Csv", import_name)
	return di.get_html_preview(import_file)

