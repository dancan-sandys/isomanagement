from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class FoodSafetyObjective(Base):
    __tablename__ = "food_safety_objectives"

    id = Column(Integer, primary_key=True, index=True)
    objective_code = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    target_value = Column(String(100))
    measurement_unit = Column(String(50))
    frequency = Column(String(100))
    responsible_person_id = Column(Integer, ForeignKey("users.id"))
    review_frequency = Column(String(100))
    last_review_date = Column(DateTime(timezone=True))
    next_review_date = Column(DateTime(timezone=True))
    status = Column(String(20), default="active")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    responsible_person = relationship("User", foreign_keys=[responsible_person_id])
    created_by_user = relationship("User", foreign_keys=[created_by])
    fsms_integrations = relationship("FSMSRiskIntegration", back_populates="food_safety_objective")

    def __repr__(self):
        return f"<FoodSafetyObjective(id={self.id}, code='{self.objective_code}', title='{self.title}')>"

