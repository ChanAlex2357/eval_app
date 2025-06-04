# Copyright (c) 2025, JACQUES Chan Alex and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from eval_app.data_management.doctype.eval_import.eval_importer import process_stack_imports, make_importer
import json

class EvalImportV3(Document):
	def start_files_import(self):
		imports = []
		imports.append(make_importer(self.emp_file, "Employee File"))
		imports.append(make_importer(self.structure_file, "Structure File"))
		imports.append(make_importer(self.salary_file, "Salary File"))

		logs = process_stack_imports(imports)
		try:
			frappe.db.set_value("Eval Import V3", self.name, "logs_data", json.dumps(logs))
		except Exception as e:
			frappe.throw(f"An error occurred during saving logs: {str(e)}")

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