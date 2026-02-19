"""
Pytest configuration and fixtures for PRP module testing
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from typing import Generator

from app.core.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.prp import PRPProgram, PRPCategory, PRPFrequency, PRPStatus


# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    """Create database engine for testing"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield engine
    # Clean up
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db(db_engine) -> Generator[Session, None, None]:
    """Database session fixture"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    """Test client fixture"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def test_role(db: Session):
    """Create a test role for testing"""
    from app.models.rbac import Role
    
    role = Role(
        name="Test Role",
        description="Test role for integration testing",
        is_default=True,
        is_editable=True,
        is_active=True
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return role

@pytest.fixture
def test_user(db: Session, test_role) -> User:
    """Create a test user for testing"""
    from app.core.security import get_password_hash
    
    user = User(
        username="test_user",
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword"),
        role_id=test_role.id,  # Use the created role ID
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_prp_program(db: Session, test_user: User) -> PRPProgram:
    """Create a test PRP program"""
    program = PRPProgram(
        program_code="TEST-PRP-001",
        name="Test PRP Program",
        description="Test program for integration testing",
        category=PRPCategory.CLEANING_AND_SANITIZING,
        objective="Ensure proper cleaning and sanitizing",
        scope="Production area",
        responsible_department="Quality Assurance",
        responsible_person=test_user.id,
        frequency=PRPFrequency.DAILY,
        sop_reference="SOP-CS-001",
        status=PRPStatus.ACTIVE,
        created_by=test_user.id
    )
    db.add(program)
    db.commit()
    db.refresh(program)
    return program
