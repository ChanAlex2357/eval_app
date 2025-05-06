# Copyright (c) 2025, JACQUES Chan Alex and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from eval_app.data_management.doctype.import_csv.import_csv import ImportCsv
from eval_app.data_management.doctype.eval_import.eval_importer import EvalImporter

class EvalImport(Document):
	def start_files_import(self):

		import_file_1 : EvalImporter = self.get_file_1_import()
		import_file_2 : EvalImporter = None
		import_file_3 : EvalImporter = None

		frappe.db.commit()

		try:
			import_file_1.start_import()
		except Exception as e:
			frappe.db.rollback()

		return import_file_1.name

	def get_import_file_csv(self, file, ref_doctype):
		import_doc : ImportCsv = frappe.new_doc("Import Csv")
		import_doc.ref_doctype = ref_doctype
		import_doc.file = file
		frappe.msgprint(f"doctype : {import_doc.ref_doctype} , file : {import_doc.file}")
		try :
			import_doc.insert()
		except Exception as e:
			raise Exception(f"Cannot instanciate and save New Import csv whith file doctype '{ref_doctype}' from : {file} ")
		return import_doc

	def get_file_1_import(self):
		if not self.file_1 :
			raise Exception("Fichier 1 - vide")
		import_file_1 =  self.get_import_file_csv(self.file_1, "File 1 - Material Request Import")

		return EvalImporter(import_file_1)

	# TODO: implementation file 2
	def get_file_2_import(self):
		if not self.file_2 :
			raise Exception("Fichier 2 - vide")
		import_file_2 =  self.get_import_file_csv(self.file_2, "File 1 - Material Request Import")

		return EvalImporter(import_file_2)
	
	# TODO: implementation file 3
	def get_file_3_import(self):
		if not self.file_3 :
			raise Exception("Fichier 3 - vide")
		import_file_3 =  self.get_import_file_csv(self.file_3, "File 1 - Material Request Import")

		return EvalImporter(import_file_3)

@frappe.whitelist()
def form_start_import(import_name: str):
	doc : EvalImport = frappe.get_single("Eval Import")
	return doc.start_files_import()