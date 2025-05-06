# Copyright (c) 2025, JACQUES Chan Alex and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.stock.doctype.material_request.material_request import make_request_for_quotation


class File3QuotationRequestSupplier(Document):
	def import_data(self):
		supplier = self.get_supplier_child()
		rfq = self.get_request_for_quotation_supplier()
		rfq.append(
			"suppliers",
			{
				"doctype": "Request For Quotation Supplier",
				"supplier": supplier.name
			}
		)

		if rfq.is_new():
			rfq.insert(ignore_permissions=True)
		else:
			rfq.save()

	def get_request_for_quotation_supplier(self):
		existing = frappe.db.exists("Request for Quotation Supplier",{"ref":self.ref})
		if existing:
			return existing

		mr = frappe.get_doc("Material Request", {"ref": self.ref})
		if not mr :
			raise Exception(f"Aucun Materiel Request avec ref {self.ref}")
		# Utilise la fonction existante pour générer le RFQ
		rfq = make_request_for_quotation(source_name=mr.name)
		return rfq

	def get_supplier_child(self):
		supplier_name = self.supplier.strip()
		exist = frappe.db.exists("Supplier", supplier_name) 
		if not exist:
			raise Exception(f"Supplier '{supplier_name}' introuvable")
		return exist


