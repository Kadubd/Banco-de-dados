from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@localhost/ze_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from sqlalchemy import Column, String, Integer, JSON
from geoalchemy2 import Geometry
from app.database import Base

class Partner(Base):
    __tablename__ = "partners"

    id = Column(String, primary_key=True, index=True)
    trading_name = Column(String, nullable=False)
    owner_name = Column(String, nullable=False)
    document = Column(String, unique=True, nullable=False)
    coverage_area = Column(Geometry("MULTIPOLYGON"), nullable=False)
    address = Column(Geometry("POINT"), nullable=False)
@router.post("/partners/")
async def create_partner(partner: PartnerSchema, db: Session = Depends(get_db)):
    if db.query(Partner).filter(Partner.document == partner.document).first():
        raise HTTPException(status_code=400, detail="Document already exists.")
    new_partner = Partner(**partner.dict())
    db.add(new_partner)
    db.commit()
    return new_partner
@router.get("/partners/{id}/")
async def get_partner(id: str, db: Session = Depends(get_db)):
    partner = db.query(Partner).filter(Partner.id == id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found.")
    return partner
from sqlalchemy import func

@router.get("/partners/search/")
async def search_partner(long: float, lat: float, db: Session = Depends(get_db)):
    point = f"SRID=4326;POINT({long} {lat})"
    partner = db.query(Partner).filter(
        func.ST_Contains(Partner.coverage_area, point)
    ).order_by(func.ST_Distance(Partner.address, point)).first()
    if not partner:
        raise HTTPException(status_code=404, detail="No partner found.")
    return partner
def test_create_partner(client):
    response = client.post("/partners/", json={...})
    assert response.status_code == 201