
from eval_app.data_management.doctype.import_csv.data_importer import DataImporter
from eval_app.data_management.doctype.import_csv.csv_importer_service import make_row_import
import frappe
from erpnext.stock.doctype.material_request.material_request import make_request_for_quotation

class File1DataImporter(DataImporter):
    
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

            ref = doc.ref  # Assure-toi que c’est bien une clé
            if ref: 
                distinct_refs.add(ref)

        # for ref in distinct_refs:
        #     try:
        #         existing = frappe.db.exists("Material Request" , {"ref":ref, "docstatus":0})
        #         if existing:
        #             mr = frappe.get_doc("Material Request", existing)
        #             mr.submit()

        #             # rfq = make_request_for_quotation(source_name=mr.name)
        #             # rfq.ref = ref
        #             # rfq.message_for_supplier = "Request for quotation message "
        #             # rfq.insert()

        #     except Exception as e:
        #         raise Exception(f"Erreur lors du submit du Material Request pour la référence {ref} : {str(e)}")

        return import_log, errors_count, success_count
