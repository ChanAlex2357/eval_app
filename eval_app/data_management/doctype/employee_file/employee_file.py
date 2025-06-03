# Copyright (c) 2025, JACQUES Chan Alex and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EmployeeFile(Document):
	def import_data(self):
		company = self.process_company()

	def process_company(self):
		# Verifier l'existance de company
		existing = frappe.db.exists("Company", self.company)
		if existing :
			return frappe.get_doc("Company",existing)
		
		company_doc = frappe.get_doc({
			"doctype":"Company",
			"country":"Madagascar",
			"company_name":self.company,
			"default_currency":"EUR"
		})
		company_doc.insert()
		return company_doc
		
			

