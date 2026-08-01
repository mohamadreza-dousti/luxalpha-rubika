from sqlalchemy import Column, Integer, String, Boolean, DateTime

from db.database import Base


class License(Base):
    __tablename__ = "licenses_pro"

    id = Column(Integer, primary_key=True, index=True)
    license_key = Column(String(255), unique=True, index=True, nullable=False)
    account_1_id = Column(String(100), nullable=True)
    account_2_id = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
