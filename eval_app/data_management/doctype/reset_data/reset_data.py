# Copyright (c) 2025, JACQUES Chan Alex and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

# Listes des tables et modules critiques à ne pas supprimer
DEFAULT_TABLES = [
    "Sales Invoice",
    "Purchase Invoice",
]
DEFAULT_MODULES = [
    "Stock",
    "Buying",
    "Selling",
]

class ResetData(Document):
    pass


# ─────────────────────────────────────────────────────────────
# FONCTIONS UTILITAIRES
# ─────────────────────────────────────────────────────────────

def is_table_deletable(doctype, exceptions):
    """Vérifie si un Doctype peut être supprimé"""
    return doctype not in exceptions


def delete_table_data(doctype):
    """Supprime les données d’un Doctype s’il existe"""
    # if frappe.db.has_table(f"tab{doctype}"):
    frappe.db.sql(f"DELETE FROM `tab{doctype}`")
        # return True
    # return False


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
    if not module:
        frappe.throw("Le module est requis pour réinitialiser les données.")

    doc_module = frappe.get_doc("Reset Data Module", module)
    exceptions = doc_module.exceptions or []
    doc_name = doc_module.label

    logs = []
    
    try:
        # Désactiver les contraintes de clé étrangère (PostgreSQL et MariaDB/MySQL)
        frappe.db.sql("SET FOREIGN_KEY_CHECKS = 0")  # pour MySQL
        # frappe.db.sql("SET CONSTRAINTS ALL DEFERRED")  # pour PostgreSQL

        # Démarrer une transaction manuelle
        frappe.db.begin()
        
        logs = reset_default_modules()
        
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
