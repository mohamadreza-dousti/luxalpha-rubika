from fastapi import Depends
from sqlalchemy.orm import Session

from db.database import get_db
from repositories.license_repository import LicenseRepository


def get_license_repo(db: Session = Depends(get_db)):
    return LicenseRepository(db)
