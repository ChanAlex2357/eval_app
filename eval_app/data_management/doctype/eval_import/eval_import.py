# Copyright (c) 2025, JACQUES Chan Alex and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from eval_app.data_management.doctype.import_csv.import_csv import ImportCsv


class EvalImport(Document):
	def start_files_import(self):
		import_file_1 = self.get_file_1_import()
		import_file_2 = None
		import_file_3 = None

	def get_import_file_csv(self, file, ref_doctype):
		import_doc : ImportCsv = frappe.new_doc("Import Csv")
		import_doc.ref_doctype = ref_doctype
		import_doc.file = file
		try :
			import_doc.insert()
		except Exception as e:
			raise Exception(f"Cannot instanciate and save New Import csv whith file doctype '{ref_doctype}' from : {file} ")
		
	def get_file_1_import(self):
		if not self.file_1 :
			raise Exception("Fichier 1 - vide")
		return self.get_import_file_csv(self.file_1, "File 1 - Material Request Import")

@frappe.whitelist()
def form_start_import(import_name: str):
	doc : EvalImport = frappe.get_single("Eval Import")
	return doc.start_files_import()