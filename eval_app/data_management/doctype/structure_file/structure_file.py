# Copyright (c) 2025, JACQUES Chan Alex and contributors
# For license information, please see license.txt

import frappe
import traceback
from frappe.model.document import Document
from eval_app.data_management.utils import *
from .StructureFileImporter import StructureFileImporter

COMPONENT_TYPE = ["earning","deduction"]

class StructureFile(Document):
	def get_data_stack_importer(self):
		return StructureFileImporter()

	def import_data(self):
		eg = ExceptionGroup("Exception group at Structure File")
		salary_structure_doc = None
		component_doc = None

		component_name = None
		component_type = None
		valeur = None
		abbr = None
		# Salary Structure process
		try:	
			salary_structure_doc = self.process_salary_structure()
		except Exception as e:
			eg.add_error(e)
		
		try :
			component_name = self.process_name()
		except Exception as e:
			eg.add_error(e)
		
		try:
			abbr = self.process_abbr()
		except Exception as e:
			eg.add_error(e)

		try:
			component_type = self.process_type()
		except Exception as e:
			eg.add_error(e)

		try:
			valeur = self.process_formula()
		except Exception as e:
			eg.add_error(e)

		try :
			component_doc = self.process_component(component_name,abbr,component_type,valeur)
		except Exception as e:
			eg.add_error(e)
	
		if eg.has_errors() :
			raise eg

		try :
			self.process_relation(salary_structure_doc, component_doc)
		except Exception as e:
			eg.add_error(e)
			raise eg

	# == Fucntion to process the structure parent ==
	def process_company(self):
		existing = frappe.db.exists("Company",self.company)
		if not existing:
			raise Exception(f"Company {self.company} doesn't exist")
		return frappe.get_doc("Company",existing)

	def process_salary_structure(self):
		company = self.process_company()
		existing = frappe.db.exists("Salary Structure", self.salary_structure)
		if existing :
			return frappe.get_doc("Salary Structure", existing)
		structure_doc = None
		try:
			structure_doc = frappe.get_doc({"doctype":"Salary Structure","name":self.salary_structure})
			structure_doc.company = company.name
			structure_doc.insert()
		except Exception as e:
			frappe.log_error(title="Salary Structure import initialisation ", message=traceback.format_exc())
			raise Exception(f"Cannot create Salary Structure {self.salary_structure},{company.name} : {str(e)}")
		return structure_doc

	# == Function to process the component == 

	def process_name(self):
		check_void_str(self.name, "Component Name")
		return self.name
	
	def process_abbr(self):
		check_void_str(self.abbr, "Component Abbr")
		return self.abbr
	
	def process_formula(self):
		check_void_str(self.valeur, "Component Formula")

		# Verifier si coherente
		return self.valeur
	
	def process_type(self):
		self.type = self.type.lower()
		check_void_str(self.type, "Component Type")

		if self.type not in COMPONENT_TYPE:
			raise Exception(f"Type {self.type} invalid , doit etre 'earning' ou 'deduction'")
		comp_type : str = self.type
		return comp_type.capitalize()
	
	def process_component(self, component_name, abbr, component_type, valeur):
		existing = frappe.db.exists("Salary Component",component_name)
		if existing:
			return frappe.get_doc("Salary Component",existing)
		
		depends_on_payment_days = True
		if valeur != "base":
			depends_on_payment_days = False
		salary_component_doc = frappe.get_doc(
			{
				"doctype":"Salary Component",
				"salary_component":component_name,
				"type":component_type,
				"salary_component_abbr":abbr,
				"formula":valeur,
				"amount_based_on_formula":True,
				"depends_on_payment_days":depends_on_payment_days
			}
		)
		salary_component_doc.insert()
		return salary_component_doc

	def process_relation(self, salary_structure, salary_component):				
		cat = None
		
		if (salary_component.type == 'Earning') and (salary_component in salary_structure.earnings):
			raise Exception(f"Salary Component {salary_component.name} est deja comprise dans les gains de {salary_structure.name} de la company {salary_structure.company}")
		elif salary_component.type == "Earning":
			cat = "earnings"

		if (salary_component.type == 'Deduction') and (salary_component in salary_structure.deductions):
			raise Exception(f"Salary Component {salary_component.name} est deja comprise dans les deductions de {salary_structure.name}")
		elif salary_component.type == "Deduction":
			cat = "deductions"

		try:
			if cat is not None :
				salary_structure.append(cat,{
					"salary_component":salary_component.name,
					"formula":salary_component.formula,
					"amount_based_on_formula":salary_component.amount_based_on_formula
				})
			salary_structure.save()
		except Exception as e:
			raise Exception(f"Cannot save the Salary Structure {salary_structure.name} in company {salary_structure.company} with component {salary_component.name} as {salary_component.type} : {str(e)}")
