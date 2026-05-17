import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class UserRole(str, enum.Enum):
    buyer = "buyer"
    seller = "seller"
    operator = "operator"
    admin = "admin"


class UserStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    banned = "banned"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(30), nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.buyer)
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.active)
    location_id = Column(
        Integer, ForeignKey("locations.id", ondelete="SET NULL"), nullable=True
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    location = relationship("Location", backref="users")
