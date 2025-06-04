

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
            "status": self.status,
            "import_logs": self.logs,
            "error_count": self.error_count,
            "success_count": self.success_count
        }

def get_resutlt_report(imports=None):
    if not imports:
        return {}
    logs = {}
    for i in range(len(imports)):
        logs.__setitem__("file_"+str(i+1),imports[i].as_dict())		
    return logs
