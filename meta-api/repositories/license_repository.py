from datetime import datetime, timezone
from sqlalchemy.orm import Session

from db.models import License


class LicenseRepository:

    def __init__(self, db: Session):
        self.db = db


    def get_license(self, license_key: str) -> License | None:
        return (
            self.db.query(License)
            .filter(License.license_key == license_key)
            .first()
        )



    def update_license(
        self,
        license_key: str,
        *,
        is_active: bool | None = None,
        account_1_id: int | None = None,
        account_2_id: int | None = None,
    ) -> License | None:

        license_obj = (
            self.db.query(License)
            .filter(License.license_key == license_key)
            .first()
        )

        if license_obj is None:
            return None

        if is_active is not None:
            license_obj.is_active = is_active

        if account_1_id is not None:
            license_obj.account_1_id = account_1_id

        if account_2_id is not None:
            license_obj.account_2_id = account_2_id

        self.db.commit()
        self.db.refresh(license_obj)

        return license_obj
