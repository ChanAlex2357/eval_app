# Copyright (c) 2025, JACQUES Chan Alex and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from eval_app.data_management.doctype.import_csv.import_csv import get_import_file_csv
from eval_app.data_management.doctype.eval_import.eval_importer import process_stack_imports


class EvalImportV3(Document):
	def start_files_import(self):
		imports = []
		imports.append(get_import_file_csv(self.emp_file, "Employee File"))
		imports.append(get_import_file_csv(self.structure_file, "Structure File"))
		imports.append(get_import_file_csv(self.salary_file, "Salary File"))

		return process_stack_imports(imports)

	def setup_files(self, emp_file, structure_file, salary_file):
		self.emp_file = emp_file
		self.structure_file = structure_file
		self.salary_file = salary_file
	
	def check_files(self):
		"""
		Check if the files are provided and valid.
		"""
		if not self.emp_file:
			return False, "Employee file is required."
		if not self.structure_file:
			return False, "Structure file is required."
		if not self.salary_file:
			return False, "Salary file is required."
		
		return True, "All files are valid."

@frappe.whitelist()
def form_start_import(source):
	import_doc : EvalImportV3 = frappe.get_doc("Eval Import V3",source)
	return import_doc.start_files_import()