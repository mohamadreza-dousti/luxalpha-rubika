import datetime
import os

from fastapi import FastAPI, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from dependencies import get_license_repo
from db.database import get_db
from middleware import AppKeyMiddleware
from schemas import RegisterLicenseRequest, CheckLicenseRequest
from repositories.license_repository import LicenseRepository

load_dotenv()

app = FastAPI()
app.add_middleware(AppKeyMiddleware)


@app.post("/register-license-pro")
def register_license(
    data: RegisterLicenseRequest,
    repo: LicenseRepository = Depends(get_license_repo)):

    license = repo.get_license(data.license_key)

    if not license:
        raise HTTPException(status_code=404, detail="license not found")
    
    if license.account_1_id == data.account_id or license.account_2_id == data.account_id:
        return {
            "message": "license refreshed",
            "success":"True"
        }

    if license.account_1_id is None:
        repo.update_license(license_key=data.license_key, account_1_id=data.account_id)
        return {
            "message": "license registered",
            "success":"True"
        }

    if license.account_2_id is None:
        repo.update_license(license_key=data.license_key, account_2_id=data.account_id)
        return {
            "message": "license registered",
            "success":"True"
        }

    
    else :
        raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "code": "LICENSE_USED",
            "message": "License already used by another account",
            "license_key": license.license_key,
            }
        )


@app.post("/check-license-pro")
def check_license(
    data: CheckLicenseRequest,
    repo: LicenseRepository = Depends(get_license_repo)):

    license = repo.get_license(data.license_key)

    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="license not found"
        )
    
    if not license.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="license disabled"
        )

    if license.expires_at and license.expires_at < datetime.date.today():

        repo.update_license(license_key=data.license_key,is_active=False)

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "LICENSE_EXPIRED",
                "message": "License expired"
            }
        )
    
    if data.account_id not in [license.account_1_id, license.account_2_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "LICENSE_BOUND",
                "message": "license bound to another account",
                "account_id": data.account_id
            }
        )


    return {
        "status":"valid",
        "message": "license is valid",
        "license": data.license_key,
    }
