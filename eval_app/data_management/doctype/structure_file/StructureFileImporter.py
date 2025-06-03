
from eval_app.data_management.doctype.import_csv.data_importer import DataImporter
from eval_app.data_management.doctype.import_csv.csv_importer_service import make_row_import
import frappe

class StructureFileImporter(DataImporter):

    def make_stack_import(self, rows, dt):
        import_log = []
        errors_count = 0
        success_count = 0
        distinct_refs = set()

        for row in rows:
            log, is_success, doc = make_row_import(row, dt)
            import_log.append(log)

            if is_success:
                success_count += 1
            else:
                errors_count += 1
            
            ref = doc.salary_structure
            if ref: 
                distinct_refs.add(ref)

        for ref in distinct_refs:
            try:
                existing = frappe.db.exists("Salary Structure",{"name":ref, "docstatus":0})
                if existing:
                    sst = frappe.get_doc("Salary Structure", existing)
                    sst.submit()
            except Exception as e:
                raise Exception(f"Cannot submit Salary Structure with name '{ref}' : {str(e)}")

        return import_log, errors_count, success_count
