
import frappe
from eval_app.data_management.utils import ExceptionGroup

def make_row_import(row, dt):
    row_data = row.as_dict()
    doc = frappe.new_doc(dt)
    try:
        # Assigner les valeurs du CSV à l'instance du Doctype
        for key, value in row_data.items():
            doc.set(key, value)

        # Si le Doctype contient une méthode `import_data`, l'exécuter
        if hasattr(doc, "import_data") and callable(doc.import_data):
            doc.import_data()
        else:
            raise ValueError("Le Doctype ne contient pas de méthode import_data")

        return {
            "row_num": row.row_num,
            "status": "Success",
            "message": f"Importation réussie la ligne {row.row_num}",
            "exception": None
        },True,doc
    except ExceptionGroup as eg:
        return {
            "row_num": row.row_num,
            "error_count":eg.errors.__len__(),
            "status": "Error",
            "message": eg.getErrorDict(),
            "exception": frappe.get_traceback()
        },False,doc
    except Exception as e:
        return {
            "row_num": row.row_num,
            "status": "Error",
            "message": [str(e)],
            "exception": frappe.get_traceback()
        },False,doc
