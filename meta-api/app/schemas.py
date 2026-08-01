from pydantic import BaseModel


class RegisterLicenseRequest(BaseModel):
    license_key: str
    account_id: str


class CheckLicenseRequest(BaseModel):
    license_key: str
    account_id: str
