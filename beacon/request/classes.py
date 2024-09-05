from strenum import StrEnum

class Granularity(StrEnum):
    BOOLEAN = "boolean",
    COUNT = "count",
    RECORD = "record"

class ErrorClass():
    def __init__(self) -> None:
        self.error_response=None
        self.error_code=None