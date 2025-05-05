# Copyright (c) 2025, JACQUES Chan Alex and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

SUPPLIER_TYPES = [
	"Company",
	"Individual",
	"Partnership"
]
class File2SupplierImport(Document):
	def import_data(self):
		# Importer ou créer le pays
		country = self.import_data_country()

		# Vérifier le type de fournisseur
		supplier_type = self.import_data_type()

		# Créer une instance de Supplier
		supplier_doc = frappe.get_doc({
			"doctype": "Supplier",
			"supplier_name": self.supplier_name,
			"supplier_type": supplier_type,
			"country": country
		})

		# Sauvegarder le fournisseur
		supplier_doc.insert(ignore_permissions=True)
		frappe.msgprint(f"Fournisseur '{self.supplier_name}' créé avec succès.")
	# = = = = = Country control = = = = =
	def import_data_country(self):
		country_name = self.country
		
		existing_country = frappe.db.exists("Country", {"country_name": country_name})

		if existing_country:
			return existing_country
		else:		
			try:
				new_country = frappe.get_doc({
					"doctype": "Country",
					"country_name": country_name,
					"code": self.set_country_code(country_name)
				})
				new_country.insert(ignore_permissions=True)
				return new_country.name
			except Exception as e:
				raise Exception("Erreur lors de la création d'un nouveau pays : " + str(e))

	def set_country_code(self, country_name):
		if not country_name or len(country_name) < 2:
			return ""
		return country_name[:2].upper()

	# = = = = = Type Control = = = = 
	def import_data_type(self):
		if self.type not in SUPPLIER_TYPES:
			raise Exception(f"La valeur '{self.type}' n'existe pas dans la liste des types de Fournisseur.")

		return self.type

			
