# Copyright (c) 2025, JACQUES Chan Alex and contributors
# For license information, please see license.txt

import frappe
from eval_app.data_management.utils import *
import datetime
from datetime import date
from frappe.utils import getdate
from frappe.model.document import Document
from erpnext.accounts.utils import FiscalYearError, get_fiscal_year
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip
from frappe.utils import cstr, getdate
from hrms.payroll.doctype.payroll_entry.payroll_entry import get_end_date

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
			pass
		except Exception as e:
			eg.add_error(e)

		if eg.has_errors():
			raise eg
		
		try:
			self.process_assignement(emp, salary_structure, mois, salaire_base)
			self.process_salary_slip(emp, salary_structure, mois)
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

	def build_salary_slip(self, emp, salary_structure, start_date):
		# starting_date = date(start_date.year, start_date.month, 1)
		end_date = get_end_date(start_date,"monthly").get("end_date")
		salary_slip:SalarySlip = make_salary_slip(
			source_name=salary_structure.name,
			employee=emp.name,
			posting_date=end_date,
		)
		return salary_slip

	def create_fiscal_year(self, base_date):
		new_fy = frappe.new_doc("Fiscal Year")
		new_fy.year_start_date = getdate(f"{base_date.year}-01-01")
		new_fy.year_end_date = getdate(f"{base_date.year}-12-31")
		new_fy.year = cstr(base_date.year)
		new_fy.insert(ignore_permissions=True)

	def process_salary_slip(self, emp, salary_structure, mois):
		try:
			date_mois = getdate(mois)
			salary_slip:SalarySlip = None
			start_month = date(mois.year, mois.month, 1)
			end_month = get_end_date(start_month,"monthly").get("end_date")
			try :
				salary_slip = self.build_salary_slip(emp, salary_structure, date_mois)
			except FiscalYearError as e :
				self.create_fiscal_year(date_mois)
				salary_slip = self.build_salary_slip(emp, salary_structure, date_mois)
		
			if not salary_slip:
				raise Exception("Salary slip not instanciated")

			salary_slip.start_date = date_mois
			salary_slip.end_date = end_month
			salary_slip.posting_date = end_month
			salary_slip.insert()
			salary_slip.submit()
		except Exception as e:
			raise Exception(f"Cannot create salary slip for {emp.first_name} {emp.last_name} to {salary_structure.name} on {mois} : {str(e)}")

	def process_assignement(self, emp, salary_sturcture, mois, salaire_base):
		try:
			start_date = date(mois.year, mois.month, 1)
			assign_salary_structure_for_employees(
				employees=[emp],
				salary_structure=salary_sturcture,
				from_date=mois,
				base=salaire_base
			)
		except Exception as e:
			raise Exception(f"Cannot create salary assignement for {emp.first_name} {emp.last_name} to {salary_sturcture.name} on {mois} : {str(e)}")

