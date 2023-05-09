class InsertDataError(Exception):
    def __init__(self, collection_name: str, data: str, error_msg: str):
        self.collection_name = collection_name
        self.data = data
        self.error_msg = error_msg

    def __str__(self) -> str:
        return f"Fail to intert data. collection: {self.collection_name}, data: {self.data}, error_msg: {self.error_msg}"


class InvalidReportTypeError(Exception):
    def __init__(self, report_type: str, monitor_name: str):
        self.report_type = report_type
        self.monitor_name = monitor_name

    def __str__(self) -> str:
        return f"Invalid report type from {self.monitor_name}. report type: {self.report_type}"


class SendMailError(Exception):
    def __init__(self, error_msg: str):
        self.error_msg = error_msg

    def __str__(self) -> str:
        return f"Fail to send report. error_msg: {self.error_msg}"


class ScriptError(Exception):
    def __init__(self, script_name: str, stderr: str):
        self.script_name = script_name
        self.stderr = stderr

    def __str__(self) -> str:
        return f"The script doesn't return zero. {self.command}. error_msg: {self.stderr}"


class ScriptUploadError(Exception):
    def __init__(self, monitor_name: str, script_name: str, error_msg: str):
        self.monitor = monitor_name
        self.script = script_name
        self.error_msg = error_msg

    def __str__(self) -> str:
        return f"Fail to upload script. monitor:{self.monitor}, script: {self.script}, error_msg:{self.error_msg}"
