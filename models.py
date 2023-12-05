# models.py

from pydantic import BaseModel

class OCRResult(BaseModel):
    identification_number: str
    name: str
    last_name: str
    date_of_birth: str
    date_of_issue: str
    date_of_expiry: str
    status: str
    timestamp: str
    
