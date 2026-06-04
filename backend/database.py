from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./cyberframe.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ThreatLog(Base):
    __tablename__ = "threat_logs"

    id = Column(Integer, primary_key=True, index=True)
    threat_id = Column(String, unique=True, index=True)
    ip_address = Column(String, index=True)
    detection_type = Column(String)
    severity = Column(String)
    status = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)
