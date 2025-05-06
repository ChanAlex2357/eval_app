from erpnext.stock.doctype.material_request.material_request import make_request_for_quotation
from eval_app.data_management.doctype.import_csv.data_importer import DataImporter
import frappe
from eval_app.data_management.doctype.import_csv.csv_importer_service import make_row_import
from erpnext.buying.doctype.request_for_quotation.request_for_quotation import make_supplier_quotation_from_rfq

class File3DataImporter(DataImporter):

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
            
            ref = doc.ref_request_quotation  # Assure-toi que c’est bien une clé
            if ref: 
                distinct_refs.add(ref)

        if errors_count == 0:
            for ref in distinct_refs:
                try:
                    rfq = frappe.get_doc("Request for Quotation", {"ref": ref, "docstatus":0})
                    rfq.submit()
                    # Generer une supplier quotation
                    sq = make_supplier_quotation_from_rfq(rfq.name)
                    sq.insert()

                except Exception as e:
                    raise Exception(f"Erreur lors du submit pour la référence {ref} : {str(e)}")

        return import_log, errors_count, success_count
