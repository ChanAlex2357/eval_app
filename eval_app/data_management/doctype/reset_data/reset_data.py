# Copyright (c) 2025, JACQUES Chan Alex and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

# Listes des tables et modules critiques à ne pas supprimer
DEFAULT_TABLES = [
    "Supplier",

    # Materiel request
    "Material Request",
    "Material Request Item",

    # Purchase Order
    "Purchase Order",
    "Purchase Order Item",

    # Request for quotation
    "Request for Quotation",
    "Request for Quotation Item",
    "Request for Quotation Supplier",

    # Supplier quotation
    "Supplier Quotation",
    "Supplier Quotation Item",

    # Purchase documents
    "Purchase Invoice",
    "Purchase Invoice Item",
    "Purchase Receipt",
    "Purchase Receipt Item",

    # Sales documents
    "Sales Invoice",
    "Sales Invoice Item",

    # Payement
    "Payment Entry",

    # Accounting
    "Journal Entry",
    "Journal Entry Account",
    "GL Entry",

    # STOCK
    "Item",
    "Item Price",
    "Stock Ledger Entry",
    "Bin",

    # Import
    "Import Csv",
    "Eval Import V3",
    # == RH ==
    "Salary Detail",
    "Salary Structure Assignment",
    "Salary Component",
    "Salary Structure",
    "Employee",
    "Employee Checkin",
    "Leave Ledger Entry",
    "Leave Allocation",
    "Leave Application",
    "Shift Assignment",
    "Additional Salary"
]

DEFAULT_MODULES = [
]

EXCEPTION_TABLES = [
    "User",
    "Role",
    "DocType",
    "Module Def",
    "Custom Field",
    "Custom DocPerm",
    "Custom Role",
    "Custom Role Profile",
    "Custom DocType",
    "Custom Module",
    "Custom Module Def",
    "Account"
]

class ResetData(Document):
    pass


# ─────────────────────────────────────────────────────────────
# FONCTIONS UTILITAIRES
# ─────────────────────────────────────────────────────────────

def is_table_deletable(doctype, exceptions):
    """Vérifie si un Doctype peut être supprimé"""
    return doctype not in EXCEPTION_TABLES


def delete_table_data(doctype):
    """Supprime les données d’un Doctype s’il existe"""
    # if frappe.db.has_table(f"tab{doctype}"):
    frappe.db.sql(f"DELETE FROM `tab{doctype}`")
        # return True
    # return False

def cancel_and_delete_entries(doctype,filters=""):
    entries = frappe.get_all(doctype, filters, pluck="name")
    for entry in entries:
        doc = frappe.get_doc(doctype, entry)
        doc.cancel()
        doc.delete()

def delete_custom_company():
    """Supprime les données de la société personnalisée"""
    try:
        # Récupère les bulletins soumis (docstatus = 1)
        cancel_and_delete_entries("Salary Slip", filters={"docstatus": 1})
        # slips = frappe.get_all("Salary Slip", filters={"docstatus": 1}, pluck="name")
        # for slip_name in slips:
        #     slip_doc = frappe.get_doc("Salary Slip", slip_name)
        #     slip_doc.cancel()   # Nécessaire avant suppression si docstatus = 1
        #     slip_doc.delete()

        
        cancel_and_delete_entries("Payroll Entry", filters={"docstatus": 1})
        # pay_entries = ("Payroll Entry", filters={"docstatus": 1}, pluck="name")
        # for pe in pay_entries:
            # pe_doc = frappe.get_doc("Payroll Entry", pe)
            # pe_doc.cancel()
            # pe_doc.delete()
        
        cancel_and_delete_entries("Attendance")

        frappe.db.commit()
        return True

    except Exception as e:
        frappe.log_error(f"Erreur lors de la suppression : {e}")
        return False

# ─────────────────────────────────────────────────────────────
# FONCTIONS DE RÉINITIALISATION
# ─────────────────────────────────────────────────────────────

def reset_table_data(doctype, exceptions = []):
	"""Supprime les données d’un Doctype"""
	logs=[]
	try:
		if not is_table_deletable(doctype, exceptions):
			return logs
		res = delete_table_data(doctype)
		if res:
			logs.append(f"Suppression des données de {doctype} réussie.")
	except Exception as e:
		logs.append(f"Erreur sur {doctype}: {e}")
	return logs

def reset_module_doc_types(module_name, exceptions = []):
    """Supprime les données de tous les DocTypes d’un module"""
    logs=[]
    dtypes = frappe.get_all("DocType", filters={"module": module_name, "custom": 0}, pluck="name")
    for dt in dtypes:
        logs = reset_table_data(dt, exceptions)
        # pass
    return logs


def reset_default_modules():
    """Supprime les données des modules définis par défaut"""
    logs=[]
    for module in set(DEFAULT_MODULES):
        logs += reset_module_doc_types(module)
    for table in set(DEFAULT_TABLES):
        logs = reset_table_data(table)
    return logs


def reset_all_modules(exceptions):
    """Réinitialise tous les modules ERPNext sauf les exceptions"""
    logs = []
    erpnext_modules = frappe.get_all("Module Def", filters={"app_name": "erpnext"}, pluck="name")
    for mod in erpnext_modules:
        logs += reset_module_doc_types(mod, exceptions)
    return logs


# ─────────────────────────────────────────────────────────────
# FONCTION PRINCIPALE EXPOSÉE
# ─────────────────────────────────────────────────────────────

@frappe.whitelist()
def reset_data(module=None):
    """
    Fonction principale appelée par le bouton de réinitialisation.
    Elle lit les paramètres du DocType 'Reset Data Module'.
    """

    logs = []
    
    try:
        # Désactiver les contraintes de clé étrangère (PostgreSQL et MariaDB/MySQL)
        frappe.db.sql("SET FOREIGN_KEY_CHECKS = 0")  # pour MySQL
        # frappe.db.sql("SET CONSTRAINTS ALL DEFERRED")  # pour PostgreSQL

        # Démarrer une transaction manuelle
        frappe.db.begin()
        
        logs = reset_default_modules()
        delete_custom_company()
        
        # Commit explicite après succès
        frappe.db.commit()

    except Exception as e:
        # Annule toute modification en cas d'erreur
        frappe.db.rollback()
        logs.append(f"Erreur: {str(e)}")

    finally:
        # Réactiver les contraintes de clé étrangère
        frappe.db.sql("SET FOREIGN_KEY_CHECKS = 1")  # pour MySQL
        # frappe.db.sql("SET CONSTRAINTS ALL IMMEDIATE")  # pour PostgreSQL
    return logs
