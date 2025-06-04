
from frappe.utils import getdate

class ExceptionGroup(Exception):
    def __init__(self,msg):
        
        self.errors = list()
        self.errors_messages = list()


    def has_errors(self):
        return len(self.errors) > 0
    
    def getErrorDict(self):
        return self.errors_messages

    def add_error(self, exception:Exception = None):
        self.errors.append(exception)
        self.errors_messages.append(str(exception))
    
    def checkpoint(self):
        if self.has_errors:
            raise self


def check_void_str(value, col_name):
    if value == None or value == "":
        raise Exception(f"La valeur de '{col_name}' ne devrais pas etre null")
    

def process_date(date_str, prop_name):
    if date_str == None or date_str  == "":
        raise Exception(f"La date '{prop_name}' ne peut pas etre null")
    process_date = getdate(validate_date_format(date_str))
    return process_date

def validate_date_format(date_str):
    from datetime import datetime
    try:
        try:
            return getdate(datetime.strptime(date_str, "%d/%m/%Y").date())
        except ValueError:
            return getdate(datetime.strptime(date_str, "%d-%m-%Y").date())
    except Exception:
        raise Exception(f"Format de date invalide : {date_str}. Format attendu : jj/mm/aaaa")

def parse_quantity(qty_str):
    try:
        qty = float(qty_str)
        if qty < 0:
            raise Exception("La quantité doit être positive")
        return qty
    except ValueError as e:
        raise Exception(f"Quantité invalide : {qty_str} | {str(e)}")