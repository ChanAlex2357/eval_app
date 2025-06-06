
import frappe
from eval_app.data_management.doctype.import_csv.import_csv import get_import_file_csv

class EvalImporter:
    def __init__(
            self,
            import_file
        ):
        self.import_file = import_file
        self.status = 0
        self.logs = []
        self.error_count = 0
        self.success_count = 0

    def start_import(self):
        result_status , import_logs, errors_count, success_count = self.import_file.start_import()

        self.status = result_status
        self.logs = import_logs
        self.error_count = errors_count
        self.success_count = success_count
    
    def commit_status(self):
        self.import_file.set_status(self.status, self.logs)

    def as_dict(self):
        return {
            "import_link":"http://erpnext.localhost:8000/app/import-csv/"+self.import_file.name,
            "import_name":self.import_file.name,
            "status": self.status,
            "import_logs": self.logs,
            "error_count": self.error_count,
            "success_count": self.success_count
        }

def make_importer(file, ref_doctype):
    """
    Factory function to create an EvalImporter instance.
    """
    import_file = get_import_file_csv(file, ref_doctype)
    return EvalImporter(import_file=import_file)

def get_resutlt_report(imports=None):
    if not imports:
        return {}
    logs = {}
    for i in range(len(imports)):
        logs.__setitem__("file_"+str(i+1),imports[i].as_dict())		
    return logs

def process_stack_imports(imports):
    frappe.db.commit()
    try:
        frappe.db.begin()

        sum_status = 0
        for import_file in imports:
            import_file.start_import()
            sum_status += import_file.status
        if sum_status != 3:
            raise Exception("Failed to import data")

        frappe.db.commit()
    except Exception as e:
        frappe.db.rollback()
        raise e
    finally:
        # commit status of import file
        for import_file in imports:
            import_file.commit_status()
        frappe.db.commit()
        return get_resutlt_report(imports)