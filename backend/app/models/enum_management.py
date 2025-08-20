from sqlalchemy import Column, String, Text, Boolean, Integer, JSON, DateTime, Index
from sqlalchemy.sql import func
from app.core.database import Base


class EnumLookupTable(Base):
    """Master table for enum lookup tables"""
    __tablename__ = "enum_lookup_tables"
    
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    module = Column(String(50), nullable=False)  # Which module this enum belongs to
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<EnumLookupTable(id={self.id}, table_name='{self.table_name}', module='{self.module}')>"


class EnumValue(Base):
    """Individual enum values"""
    __tablename__ = "enum_values"
    
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(100), nullable=False, index=True)
    value = Column(String(100), nullable=False)
    display_name = Column(String(200), nullable=False)
    description = Column(Text)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, index=True)
    is_default = Column(Boolean, default=False)
    enum_metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Create unique constraint on table_name + value
    __table_args__ = (
        Index('idx_enum_values_table_value', 'table_name', 'value', unique=True),
    )
    
    def __repr__(self):
        return f"<EnumValue(id={self.id}, table_name='{self.table_name}', value='{self.value}', display_name='{self.display_name}')>"
