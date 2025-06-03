# Copyright (c) 2025, JACQUES Chan Alex and contributors
# For license information, please see license.txt

import frappe
from eval_app.data_management.utils import *
from frappe.model.document import Document


class SalaryFile(Document):
	def import_data(self):
		eg:ExceptionGroup = ExceptionGroup("Exception Group at Salary File")

		mois = None
		emp = None
		salaire_base = None
		salary_structure = None
		try:
			emp = self.process_emp()
		except Exception as e:
			eg.add_error(e)

		if eg.has_errors():
			raise eg
		
		try:
			salary_structure = self.process_assignement(emp, salary_structure, mois, salaire_base)
		except Exception as e:
			eg.add_error(e)
			raise eg
	
	def process_emp(self):
		existing = frappe.db.exists("Employee",{"emp_ref":self.ref_employe})
		if not existing:
			raise Exception(f"Employee with ref {self.ref_employe} not found")
		return frappe.get_doc("Employee",existing)


	def process_assignement(self, emp, salary_sturcture, mois, salaire_base):
		pass

