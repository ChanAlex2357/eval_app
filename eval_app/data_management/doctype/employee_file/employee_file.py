# Copyright (c) 2025, JACQUES Chan Alex and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate
from eval_app.data_management.utils import *
import traceback

class EmployeeFile(Document):
	def import_data(self):
		eg = ExceptionGroup("Exception group at EmployeeFile")
		company = None
		nom  = None
		prenom = None
		date_embauche = None
		date_naissance = None
		genre = None

		# Company Process
		try:
			company = self.process_company()
		except Exception as e:
			eg.add_error(e)
		# Full Name Process
		try:
			nom, prenom = self.process_full_name()
		except Exception as e:
			eg.add_error(e)
		
		# Date Embauche
		try:
			date_embauche = self.process_embauche()
		except Exception as e:
			eg.add_error(e)

		# Date Naissance
		try:
			date_naissance = self.process_naissance()
		except Exception as e:
			eg.add_error(e)
		# Genre process
		try:
			genre = self.process_genre()
		except Exception as e:
			eg.add_error(e)
		
		if eg.has_errors() :
			raise eg

		try :
			emp = frappe.get_doc({
				"doctype":"Employee",
				"last_name":prenom,
				"first_name":nom,
				"company":company,
				"date_of_joining":date_embauche,
				"date_of_birth":date_naissance,
				"gender":genre
			})
			emp.insert()
		except Exception as e :
			frappe.log_error(
            	title=f"Employee during import {self.name}",
            	message=traceback.format_exc()
        	)
			eg.add_error(e)
			raise eg

	def process_company(self):
		# Verifier l'existance de company
		existing = frappe.db.exists("Company", self.company)
		if existing :
			return frappe.get_doc("Company",existing)
		
		try :
			company_doc = frappe.get_doc({
				"doctype":"Company",
				"country":"Madagascar",
				"company_name":self.company,
				"default_currency":"EUR",
				"default_holiday_list":"HL"
			})
			company_doc.insert()
			return company_doc
		except Exception as e:
			frappe.log_error(title=f"Import {self.name} Employee.Company",message=traceback.format_exc())
			raise Exception(f"Cannot create Company {self.company} : {str(e)}")
		
	def process_full_name(self):
		check_void_str(self.nom, "Nom")
		check_void_str(self.prenom, "Prenom")

		return self.nom, self.prenom
	
	def process_embauche(self):
		return process_date(self.date_embauche, "Date Embauche")

	def process_naissance(self):
		return process_date(self.date_naissance, "Date Naissance")
	
	def process_genre(self):
		check_void_str(self.genre, "Genre")

		existing = frappe.db.exists("Gender", self.genre)
		if existing:
			return frappe.get_doc("Gender",existing)
		try:
			genre_doc = frappe.get_doc({"doctype":"Gender","gender":self.genre})
			genre_doc.insert()
			return genre_doc
		except Exception as e:
			frappe.log_error(
				title = f"Import {self.name} Employee.Genre",
				message = traceback.format_exc()
			)
			raise Exception(f"Cannot create Gender {self.genre} : {str(e)}")