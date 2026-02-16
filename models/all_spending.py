from sqlalchemy import Column, String, DateTime, Float
from models.base import Base

class AllSpending(Base):
    __tablename__ = "AllSpending"
    RowID = Column(String(8), primary_key=True)
    Date = Column(DateTime, nullable=False)
    Description = Column(String(255), nullable=False)
    Subdescription = Column(String(255), nullable=True)
    Amount = Column(Float, nullable=False)
    Source = Column(String(50), nullable=False)
    File = Column(String(255), nullable=False)
    Balance = Column(Float, nullable=True)
    Category = Column(String(50), nullable=True)

    def __repr__(self):
        return f"<AllSpending(RowID='{self.RowID}', Date='{self.Date}', Description='{self.Description}', Amount={self.Amount})>"

