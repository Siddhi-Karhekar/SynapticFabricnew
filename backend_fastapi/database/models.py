from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime

from backend_fastapi.database.database import Base


class MachineLog(Base):

    __tablename__ = "machine_logs"

    id = Column(Integer, primary_key=True, index=True)

    timestamp = Column(DateTime, default=datetime.utcnow)

    machine_id = Column(String)

    temperature = Column(Float)

    torque = Column(Float)

    tool_wear = Column(Float)

    vibration_index = Column(Float)

    anomaly_score = Column(Float)

    health_status = Column(String)

    failure_probability = Column(Float)