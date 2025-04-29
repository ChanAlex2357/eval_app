import frappe
from frappe import _
from frappe.model.document import Document
import csv
from frappe.utils.file_manager import get_file_path
from frappe.utils.csvutils import read_csv_content

class CsvImporter:
    def __init__(self, doctype, file_path, csv_import=None):
        self.csv_import = csv_import
        self.doctype = doctype

        if not file_path and csv_import and csv_import.file:
            file_path = get_file_path(csv_import.file)

        self.file_path = file_path
        self.csv_file = CsvFile(self.file_path, doctype)

    def parse_file(self):
        return self.csv_file.get_preview()


class Header:
    def __init__(self, raw_headers):
        self.raw_headers = raw_headers
        self.normalized_headers = self._normalize_headers(raw_headers)

    def _normalize_headers(self, headers):
        # Normalisation simple (peut être améliorée)
        return [h.strip().lower().replace(" ", "_") for h in headers]

    def get_fields(self):
        return self.normalized_headers


class Row:
    def __init__(self,index, data, header: Header):
        self.idx = index
        self.row_num = self.idx + 1
        self.data = data
        self.header = header

    def as_dict(self):
        return dict(zip(self.header.get_fields(), self.data))


class CsvFile:
    def __init__(self, file_path, doctype=None):
        self.file_path = file_path
        self.doctype = doctype
        self.header = None
        self.rows = []

        self._parse()
    
    
    

    def _parse(self):
        file_name = frappe.db.get_value("File", {"file_url": self.file_path})
        
        if not file_name:
            raise FileNotFoundError(f"Aucun fichier trouvé avec file_url = {self.file_path}")
        
        file = frappe.get_doc("File", file_name)
        file_content = file.get_content()
        
        raw_data = read_csv_content(file_content,True)
        
        if not raw_data:
            raise ValueError("CSV file is empty")


        raw_header = raw_data[0]
        self.header = Header(raw_header)
        self.rows = [Row(idx,row, self.header) for idx, row in enumerate(raw_data[1:]) if any(row)]

    def get_preview(self):
        return {
            "columns": self.header.get_fields(),
            "data": [row.data for row in self.rows]
        }

    def get_objects(self):
        return [row.as_dict() for row in self.rows]
