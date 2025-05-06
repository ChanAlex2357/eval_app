

class EvalImporter:
    def __init__(
            self,
            import_file
        ):
        self.import_file = import_file
        self.status = None
        self.logs = []
        self.error_count = 0
        self.success_count = 0

    def start_import(self):
        result_status , import_logs, errors_count, success_count = self.import_file.start_import()

        self.status = result_status
        self.logs = import_logs
        self.error_count = errors_count
        self.success_count = success_count
    
    def commit_status():
        pass