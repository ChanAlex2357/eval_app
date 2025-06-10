
from frappe.utils import getdate
from datetime import datetime
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
    process_date = (validate_date_format(date_str))
    return process_date


def validate_date_format(date_str):
    """
    Tente de parser une date depuis une chaîne selon différents formats courants.
    Renvoie une date au format Frappe.
    """
    formats = ["%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%Y-%m-%d", "%d.%m.%Y"]
    
    for fmt in formats:
        try:
            return getdate(datetime.strptime(date_str.strip(), fmt).date())
        except ValueError:
            continue

    raise Exception(f"Format de date invalide : '{date_str}'. Formats attendus : {', '.join(formats)}")

import re

def parse_quantity(val):
    if isinstance(val, (int, float)):
        return float(val)
    val = str(val).replace(" ", "").replace(",", ".").replace('"', '').replace("'", '')
    val = re.sub(r"[^\d\.]", "", val)  # garde que les chiffres et les points
    try:
        return float(val)
    except ValueError:
        raise Exception(f"Invalid amount: '{val}'")
