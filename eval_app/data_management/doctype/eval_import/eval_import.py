# Copyright (c) 2025, JACQUES Chan Alex and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from eval_app.data_management.doctype.import_csv.import_csv import ImportCsv
from eval_app.data_management.doctype.eval_import.eval_importer import EvalImporter

class EvalImport(Document):
	def start_files_import(self):
		imports = []
		imports.append	(self.get_file_1_import())
		imports.append	(self.get_file_2_import())
		imports.append	(self.get_file_3_import())

		frappe.db.commit()

		try:
			frappe.db.begin()

			sum_status = 0
			for import_file in imports:
				import_file.start_import()
				sum_status += import_file.status
			if sum_status != 3:
				raise Exception("Failed to import data")

			frappe.db.commit()
		except Exception as e:
			frappe.db.rollback()
			raise e
		finally:
			# commit status of import file
			for import_file in imports:
				import_file.commit_status()
			frappe.db.commit()
			return self.get_resutlt_report(imports)


		

	def get_resutlt_report(self,imports=None):
		if not imports:
			return {}
		logs = {}
		for i in range(len(imports)):
			logs.__setitem__("file_"+str(i+1),imports[i].as_dict())		
		return logs

	def get_import_file_csv(self, file, ref_doctype):
		import_doc : ImportCsv = frappe.new_doc("Import Csv")
		import_doc.ref_doctype = ref_doctype
		import_doc.file = file

		try :
			import_doc.insert()
		except Exception as e:
			raise Exception(f"Cannot instanciate and save New Import csv whith file doctype '{ref_doctype}' from : {file} ")
		return import_doc

	def get_file_1_import(self):
		if not self.file_1 :
			raise Exception("Fichier 1 - vide")
		import_file_1 =  self.get_import_file_csv(self.file_1, "File 1 - Material Request Import")

		return EvalImporter(import_file=import_file_1)

	# TODO: implementation file 2
	def get_file_2_import(self):
		if not self.file_2 :
			raise Exception("Fichier 2 - vide")
		import_file_2 =  self.get_import_file_csv(self.file_2, "File 2 - Supplier Import")

		return EvalImporter(import_file_2)
	
	# TODO: implementation file 3
	def get_file_3_import(self):
		if not self.file_3 :
			raise Exception("Fichier 3 - vide")
		import_file_3 =  self.get_import_file_csv(self.file_3, "File 3 - Quotation Request Supplier")

		return EvalImporter(import_file_3)

@frappe.whitelist()
def form_start_import(import_name: str):
	doc : EvalImport = frappe.get_single("Eval Import")
	return doc.start_files_import()