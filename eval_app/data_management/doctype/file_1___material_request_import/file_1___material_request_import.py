from frappe.model.document import Document
import frappe

from frappe.utils import getdate
from eval_app.data_management.doctype.file_1___material_request_import.file_1_data_importer import File1DataImporter

class File1MaterialRequestImport(Document):
	# def get_data_stack_importer(self):
	# 	return File1DataImporter()

	def import_data(self):
		try:

			# Traitement 1 : Item
			item_doc = self.import_item()

			# Traitement 2 : Material Request
			request_doc = self.import_material_request()
			
			# Traitement 3 : Material Request Item
			self.import_material_request_item(request_doc, item_doc)

			if request_doc.is_new() :
				request_doc.insert(ignore_permissions=True)
			else:
				frappe.log("Saved ")
				request_doc.save(ignore_permissions=True)
				
		except Exception as e:
			frappe.log_error(str(e), "Erreur Import Material Request")
			raise e

	def import_material_request(self):

		ref = str(int(self.ref))
		purpose = self.purpose
		date = self.date  # format attendu : jj/mm/yyyy

		# Vérifier et parser la date
		try:
			date = getdate(self.validate_date_format(date))
		except Exception:
			raise Exception(f"Date invalide : {self.date}. Format attendu : jj/mm/yyyy")

		# Vérifier si purpose existe
		valid_purposes = ["Purchase", "Material Transfer", "Material Issue", "Manufacture"]
		if purpose not in valid_purposes:
			raise Exception(f"Purpose invalide : {purpose}. Choix valides : {valid_purposes}")

		# Vérifier si une MR avec la référence existe déjà
		existing = frappe.db.exists("Material Request", {"ref": ref})
		if existing:
			return frappe.get_doc("Material Request", existing)

		# Création
		mr = frappe.get_doc({
			"doctype": "Material Request",
			"title": "MR - " + ref,
			"transaction_date": date,
			"schedule_date": date,
			"material_request_type": purpose,
			"company": frappe.defaults.get_user_default("Company"),
			"ref":ref
		})
		return mr

	def import_item(self):
		import frappe

		item_name = self.item_name
		item_group = self.item_groupe
		
		# Créer item si inexistant
		item = frappe.db.exists("Item", {"item_name": item_name})
		if item:
			return frappe.get_doc("Item", item)

		# Créer group si inexistant
		if not frappe.db.exists("Item Group", item_group):
			group = frappe.get_doc({
				"doctype": "Item Group",
				"item_group_name": item_group,
				"is_group": 0
			})
			frappe.msgprint('Group created : '+group.item_group_name)
			
			group.insert(ignore_permissions=True)

		# Sinon créer item
		new_item = frappe.get_doc({
			"doctype": "Item",
			"item_code": item_name,
			"item_name": item_name,
			"item_group": item_group,
			"stock_uom": "Unit",  # à adapter si nécessaire
			"is_stock_item": 1,
			"disabled": 0
		})
		new_item.insert(ignore_permissions=True)
		new_item.submit()

		return new_item
	
	def get_warehouse(self):
		warehouse_result = frappe.db.exists("Warehouse",{"warehouse_name": self.target_warehouse})
		if not warehouse_result:
			warehouse= frappe.get_doc({
				"doctype": "Warehouse",
				"warehouse_name":self.target_warehouse,
				"company":frappe.defaults.get_user_default("Company")
			})
			warehouse.insert()
			return warehouse

		return frappe.get_doc("Warehouse",warehouse_result)

	def import_material_request_item(self, request_doc, item_doc):
		warehouse = self.get_warehouse()
		quantity = self.parse_quantity(self.quantity)
		required_by = self.validate_date_format(self.required_by)

		# Date requise >= date MR
		if getdate(required_by) < getdate(request_doc.transaction_date):
			raise Exception(f"La date de besoin ({required_by}) est avant la date de la demande ({request_doc.transaction_date})")

		# Ajouter une ligne d'article à la MR
		request_doc.append("items", {
			"item_code": item_doc.name,
			"qty": quantity,
			"schedule_date": getdate(required_by),
			"warehouse": warehouse.name
		})

	# ========== Utils ==========
	def validate_date_format(self, date_str):
		from datetime import datetime
		try:
			try:
				return datetime.strptime(date_str, "%d/%m/%Y").date()
			except ValueError:
				return datetime.strptime(date_str, "%d-%m-%Y").date()
		except Exception:
			raise Exception(f"Format de date invalide : {date_str}. Format attendu : jj/mm/aaaa")

	def parse_quantity(self, qty_str):
		try:
			qty = float(qty_str)
			if qty < 0:
				raise Exception("La quantité doit être positive")
			return qty
		except ValueError as e:
			raise Exception(f"Quantité invalide : {qty_str} | {str(e)}")
