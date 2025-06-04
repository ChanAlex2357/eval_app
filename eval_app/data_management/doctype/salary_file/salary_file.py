# Copyright (c) 2025, JACQUES Chan Alex and contributors
# For license information, please see license.txt

import frappe
from eval_app.data_management.utils import *
import datetime
from frappe.utils import getdate
from frappe.model.document import Document
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip 
from hrms.payroll.doctype.salary_structure.salary_structure import assign_salary_structure_for_employees, make_salary_slip

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

		try:
			mois = self.process_mois()
		except Exception as e:
			eg.add_error(e)

		try:
			salaire_base = self.process_salary_amount()
		except Exception as e:
			eg.add_error(e)

		try:
			salary_structure = self.process_salary_structure(emp)
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

	def process_mois(self):
		return process_date(self.mois, "Mois")
	
	def process_salary_amount(self):
		salary = parse_quantity(self.salaire_base)

		return salary
	
	def process_salary_structure(self, emp):
		if emp == None:
			raise Exception("Cannot check the salary structure without valid Employee")
		
		existing = frappe.db.exists("Salary Structure",{"name":self.salaire,"company":emp.company})
		if not existing:
			raise Exception(f"Aucune Salary Structure trouver pour '{self.salaire}' dans la company '{emp.company}'")
		return frappe.get_doc("Salary Structure", existing)

	def process_assignement(self, emp, salary_sturcture, mois, salaire_base):
		try:
			assign_salary_structure_for_employees(
				employees=[emp],
				salary_structure=salary_sturcture,
				from_date=mois,
				base=salaire_base
			)
		except Exception as e:
			raise Exception(f"Cannot create salary assignement for {emp.first_name} {emp.last_name} to {salary_sturcture.name} on {mois} : {str(e)}")

		try:
			salary_slip:SalarySlip = make_salary_slip(
				source_name=salary_sturcture.name,
				employee=emp.name,
				posting_date=getdate(mois),
			)

			salary_slip.start_date = mois
			salary_slip.insert()
			salary_slip.submit()
		except Exception as e:
			raise Exception(f"Cannot create salary slip for {emp.first_name} {emp.last_name} to {salary_sturcture.name} on {mois} : {str(e)}")
