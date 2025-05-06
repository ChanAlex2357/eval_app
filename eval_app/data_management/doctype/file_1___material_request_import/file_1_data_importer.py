
from eval_app.data_management.doctype.import_csv.data_importer import DataImporter
from eval_app.data_management.doctype.import_csv.csv_importer_service import make_row_import
import frappe

class File1DataImporter(DataImporter):
    
    def make_stack_import(self, rows, dt):
        import_log = [] 
        errors_count = 0
        success_count = 0

        for row in rows:
            log, is_success, doc = make_row_import(row, dt)
            import_log.append(log)

            if is_success:
                success_count += 1
            else:
                errors_count += 1

        return import_log, errors_count, success_count
