# Copyright (c) 2025, JACQUES Chan Alex and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ItemImportCsv(Document):
    def import_data(self):
        # Create new Item Doc
        item_doc = frappe.new_doc("Item")
        item_doc.item_code = self.code
        item_doc.item_name = self.code
        
        # Create the group item
        group_doc = self.import_group()
        item_doc.item_group = group_doc.name
        
        item_doc.insert()
        
    def import_group(self):
        docs = group_doc = frappe.get_all("Item Group", filters = {"item_group_name":self.group})
        if docs.__len__() > 0 :
            return docs[0]
        # Create new group if doesn't exist
        return frappe.get_doc({
				"doctype": "Item Group",
				"item_group_name": self.group,
				"is_group": 0
			}).insert()