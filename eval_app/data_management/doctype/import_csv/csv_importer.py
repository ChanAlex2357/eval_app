
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.core.doctype.data_import.importer import ImportFile

class CsvImporter:
    def __init__(self, doctype, file_path, csv_import = None):
        self.csv_import = csv_import
        self.doctype = doctype
        self.import_file = ImportFile(
			doctype,
			file_path or self.csv_import.file
		)