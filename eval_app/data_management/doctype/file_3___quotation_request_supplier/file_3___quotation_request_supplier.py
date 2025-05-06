# Copyright (c) 2025, JACQUES Chan Alex and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from eval_app.data_management.doctype.file_3___quotation_request_supplier.file_3_data_importer import File3DataImporter
from erpnext.stock.doctype.material_request.material_request import make_request_for_quotation


class File3QuotationRequestSupplier(Document):
	def get_data_stack_importer(self):
		return File3DataImporter()

	def import_data(self):
		supplier = self.get_supplier_child()
		rfq = self.get_request_for_quotation()
		rfq.append(
			"suppliers",
			{
				"doctype": "Request For Quotation Supplier",
				"supplier": supplier.name
			}
		)

		if rfq.is_new():
			rfq.message_for_supplier = "Request for quotation message "
			rfq.insert(ignore_permissions=True)
		else:
			rfq.save()

	def get_request_for_quotation(self):
		ref = self.ref_request_quotation
		existing = frappe.db.exists("Request for Quotation",{"ref":ref, "docstatus":0})
		if existing:
			return frappe.get_doc("Request for Quotation",existing)
		
		try:
			mr = frappe.get_doc("Material Request", {"ref": ref, "docstatus":0})
			if not mr :
				raise Exception(f"Aucun Materiel Request avec ref {ref} pour le contexte de l'import")
			mr.submit()

			# Utilise la fonction existante pour générer le RFQ
			rfq = make_request_for_quotation(source_name=mr.name)
			rfq.ref = ref
		except Exception as e:
			raise Exception(f" Erreur instanciation du Request for Quotation parent avec ref {ref} : {str(e)}")

		return rfq

	def get_supplier_child(self):
		supplier_name = self.supplier.strip()
		exist = frappe.db.exists("Supplier", supplier_name) 
		if not exist:
			raise Exception(f"Supplier '{supplier_name}' introuvable")
		return  frappe.get_doc("Supplier", exist)


