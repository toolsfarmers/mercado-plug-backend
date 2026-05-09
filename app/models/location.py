from sqlalchemy import Column, Integer, String, Text

from app.database import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    country = Column(String(100), nullable=False, default="República Dominicana")
    province = Column(String(100), nullable=False)
    municipality = Column(String(100), nullable=True)
    sector = Column(String(150), nullable=True)
    address_line = Column(String(255), nullable=True)
    reference_point = Column(Text, nullable=True)
    additional_details = Column(Text, nullable=True)
