# Copyright (c) 2025, JACQUES Chan Alex and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EvalImportV3(Document):
	def start_files_import(self):
		pass
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
def start_import():
	import_doc : EvalImportV3 = EvalImportV3()
	return import_doc.start_files_import()