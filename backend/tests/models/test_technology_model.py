# File: tests/models/test_technology_model.py
import pytest
import uuid
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.models.technology import (
    BigTechComponent, UberTechComponent, UniversalProject, 
    TechRequirement, ProjectDevelopment, TechnologyOwnership,
    ProjectComponentAssignment
)

class TestBigTechComponentModel:
    """Tests for the BigTechComponent model."""
    
    def test_create_big_tech(self, db_session):
        """Test creating a Big Tech component."""
        # Create a Big Tech component
        big_tech = BigTechComponent(
            name="Test Big Tech",
            description="A test Big Tech component",
            tech_group="A"
        )
        
        db_session.add(big_tech)
        db_session.commit()
        db_session.refresh(big_tech)
        
        # Verify the Big Tech component was created
        assert big_tech.id is not None
        assert big_tech.name == "Test Big Tech"
        assert big_tech.description == "A test Big Tech component"
        assert big_tech.tech_group == "A"
        assert isinstance(big_tech.created_at, datetime)
    
    def test_unique_big_tech_name(self, db_session):
        """Test that Big Tech component names must be unique."""
        # Create a Big Tech component
        big_tech1 = BigTechComponent(
            name="Unique Big Tech",
            tech_group="B"
        )
        
        db_session.add(big_tech1)
        db_session.commit()
        
        # Try to create another Big Tech component with the same name
        big_tech2 = BigTechComponent(
            name="Unique Big Tech",
            tech_group="C"
        )
        
        db_session.add(big_tech2)
        
        # This should raise an integrity error due to the unique constraint
        with pytest.raises(IntegrityError):
            db_session.commit()

class TestUberTechComponentModel:
    """Tests for the UberTechComponent model."""
    
    def test_create_uber_tech(self, db_session):
        """Test creating an Uber-Tech component."""
        # Create an Uber-Tech component
        uber_tech = UberTechComponent(
            name="Test Uber Tech",
            description="A test Uber-Tech component"
        )
        
        db_session.add(uber_tech)
        db_session.commit()
        db_session.refresh(uber_tech)
        
        # Verify the Uber-Tech component was created
        assert uber_tech.id is not None
        assert uber_tech.name == "Test Uber Tech"
        assert uber_tech.description == "A test Uber-Tech component"
        assert isinstance(uber_tech.created_at, datetime)
    
    def test_unique_uber_tech_name(self, db_session):
        """Test that Uber-Tech component names must be unique."""
        # Create an Uber-Tech component
        uber_tech1 = UberTechComponent(
            name="Unique Uber Tech"
        )
        
        db_session.add(uber_tech1)
        db_session.commit()
        
        # Try to create another Uber-Tech component with the same name
        uber_tech2 = UberTechComponent(
            name="Unique Uber Tech"
        )
        
        db_session.add(uber_tech2)
        
        # This should raise an integrity error due to the unique constraint
        with pytest.raises(IntegrityError):
            db_session.commit()

class TestUniversalProjectModel:
    """Tests for the UniversalProject model."""
    
    def test_create_universal_project(self, db_session):
        """Test creating a Universal Project."""
        # Create a Universal Project
        project = UniversalProject(
            name="Test Universal Project",
            description="A test Universal Project",
            beneficiaries=["Thrizoth", "Glacian Current"],
            harmed=["Methane Collective", "Silicon Liberation"]
        )
        
        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)
        
        # Verify the Universal Project was created
        assert project.id is not None
        assert project.name == "Test Universal Project"
        assert project.description == "A test Universal Project"
        assert project.beneficiaries == ["Thrizoth", "Glacian Current"]
        assert project.harmed == ["Methane Collective", "Silicon Liberation"]
        assert isinstance(project.created_at, datetime)
    
    def test_unique_universal_project_name(self, db_session):
        """Test that Universal Project names must be unique."""
        # Create a Universal Project
        project1 = UniversalProject(
            name="Unique Universal Project"
        )
        
        db_session.add(project1)
        db_session.commit()
        
        # Try to create another Universal Project with the same name
        project2 = UniversalProject(
            name="Unique Universal Project"
        )
        
        db_session.add(project2)
        
        # This should raise an integrity error due to the unique constraint
        with pytest.raises(IntegrityError):
            db_session.commit()

class TestTechRequirementModel:
    """Tests for the TechRequirement model."""
    
    @pytest.fixture
    def game_id(self, db_session):
        """Create a game and return its ID for testing."""
        from app.models.game import Game
        from app.schemas.enums import GameStatus
        
        # Create a game in the database
        game = Game(
            name="Test Game",
            status=GameStatus.SETUP,
            current_round=1
        )
        db_session.add(game)
        db_session.commit()
        db_session.refresh(game)
        return game.id

    @pytest.fixture
    def owner_id(self, db_session, game_id):
        """Create a civilization and return its ID for testing."""
        from app.models.civilization import Civilization
        from app.schemas.enums import CivilizationName
        
        # Create a civilization in the database
        civ = Civilization(
            game_id=game_id,
            name=CivilizationName.THRIZOTH,
            display_name="The Thrizoth"
        )
        db_session.add(civ)
        db_session.commit()
        db_session.refresh(civ)
        return civ.id
    
    @pytest.fixture
    def required_tech_id(self, db_session):
        """Create a BigTech component and return its ID for testing."""
        # Create a BigTech component to use as a required_tech_id
        big_tech = BigTechComponent(
            name=f"Required Tech {uuid.uuid4()}",
            description="A required tech component",
            tech_group="A"
        )
        
        db_session.add(big_tech)
        db_session.commit()
        db_session.refresh(big_tech)
        return big_tech.id
    
    @pytest.fixture
    def tech_id(self, db_session):
        """Create an UberTech component and return its ID for testing."""
        # Create an UberTech component to use as a tech_id
        uber_tech = UberTechComponent(
            name=f"Tech {uuid.uuid4()}",
            description="A tech component"
        )
        
        db_session.add(uber_tech)
        db_session.commit()
        db_session.refresh(uber_tech)
        return uber_tech.id
    
    def test_create_tech_requirement(self, db_session, tech_id, required_tech_id):
        """Test creating a technology requirement."""
        # Create a technology requirement
        requirement = TechRequirement(
            tech_type="uber_tech",
            tech_id=tech_id,
            required_tech_type="big_tech",
            required_tech_id=required_tech_id,
            quantity=1
        )
        
        db_session.add(requirement)
        db_session.commit()
        db_session.refresh(requirement)
        
        # Verify the technology requirement was created
        assert requirement.id is not None
        assert requirement.tech_type == "uber_tech"
        assert requirement.tech_id == tech_id
        assert requirement.required_tech_type == "big_tech"
        assert requirement.required_tech_id == required_tech_id
        assert requirement.quantity == 1
    
    
    
    def test_unique_tech_requirement(self, db_session, tech_id, required_tech_id):
        """Test that technology requirements must be unique."""
        # Create a technology requirement
        requirement1 = TechRequirement(
            tech_type="uber_tech",
            tech_id=tech_id,
            required_tech_type="big_tech",
            required_tech_id=required_tech_id,
            quantity=1
        )
        
        db_session.add(requirement1)
        db_session.commit()
        
        # Try to create another technology requirement with the same tech and required tech
        requirement2 = TechRequirement(
            tech_type="uber_tech",
            tech_id=tech_id,
            required_tech_type="big_tech",
            required_tech_id=required_tech_id,
            quantity=2
        )
        
        db_session.add(requirement2)
        
        # This should raise an integrity error due to the unique constraint
        with pytest.raises(IntegrityError):
            db_session.commit()

class TestProjectDevelopmentModel:
    """Tests for the ProjectDevelopment model."""
    
    @pytest.fixture
    def game_id(self, db_session):
        """Create a game and return its ID for testing."""
        from app.models.game import Game
        from app.schemas.enums import GameStatus
        
        game = Game(
            name="Test Game",
            status=GameStatus.SETUP,
            current_round=1
        )
        db_session.add(game)
        db_session.commit()
        db_session.refresh(game)
        return game.id

    @pytest.fixture
    def civilization_id(self, db_session, game_id):
        """Create a civilization and return its ID for testing."""
        from app.models.civilization import Civilization
        from app.schemas.enums import CivilizationName
        
        civ = Civilization(
            game_id=game_id,
            name=CivilizationName.THRIZOTH,
            display_name="The Thrizoth"
        )
        db_session.add(civ)
        db_session.commit()
        db_session.refresh(civ)
        return civ.id
    
    @pytest.fixture
    def project_id(self):
        """Generate a project ID for testing."""
        return uuid.uuid4()
    
    def test_create_project_development(self, db_session, game_id, civilization_id, project_id):
        """Test creating a project development."""
        # Create a project development
        project_dev = ProjectDevelopment(
            game_id=game_id,
            civilization_id=civilization_id,
            project_type="universal",
            project_id=project_id,
            current_phase="research",
            progress_percentage=0.0
        )
        
        db_session.add(project_dev)
        db_session.commit()
        db_session.refresh(project_dev)
        
        # Verify the project development was created
        assert project_dev.id is not None
        assert project_dev.game_id == game_id
        assert project_dev.civilization_id == civilization_id
        assert project_dev.project_type == "universal"
        assert project_dev.project_id == project_id
        assert project_dev.current_phase == "research"
        assert project_dev.progress_percentage == 0.0
        assert isinstance(project_dev.started_at, datetime)
        assert project_dev.completed_at is None
        assert project_dev.is_sabotaged is False
        assert project_dev.sabotage_round is None
    
    def test_unique_civilization_project(self, db_session, game_id, civilization_id, project_id):
        """Test that a civilization can't develop the same project twice."""
        # Create a project development
        project_dev1 = ProjectDevelopment(
            game_id=game_id,
            civilization_id=civilization_id,
            project_type="universal",
            project_id=project_id,
            current_phase="research",
            progress_percentage=0.0
        )
        
        db_session.add(project_dev1)
        db_session.commit()
        
        # Try to create another project development for the same civilization and project
        project_dev2 = ProjectDevelopment(
            game_id=game_id,
            civilization_id=civilization_id,
            project_type="universal",
            project_id=project_id,
            current_phase="prototype",
            progress_percentage=10.0
        )
        
        db_session.add(project_dev2)
        
        # This should raise an integrity error due to the unique constraint
        with pytest.raises(IntegrityError):
            db_session.commit()

class TestTechnologyOwnershipModel:
    """Tests for the TechnologyOwnership model."""
    
    @pytest.fixture
    def game_id(self, db_session):
        """Create a game and return its ID for testing."""
        from app.models.game import Game
        from app.schemas.enums import GameStatus
        
        game = Game(
            name="Test Game",
            status=GameStatus.SETUP,
            current_round=1
        )
        db_session.add(game)
        db_session.commit()
        db_session.refresh(game)
        return game.id

    @pytest.fixture
    def owner_id(self, db_session, game_id):
        """Create a civilization and return its ID for testing."""
        from app.models.civilization import Civilization
        from app.schemas.enums import CivilizationName
        
        civ = Civilization(
            game_id=game_id,
            name=CivilizationName.THRIZOTH,
            display_name="The Thrizoth"
        )
        db_session.add(civ)
        db_session.commit()
        db_session.refresh(civ)
        return civ.id
    
    @pytest.fixture
    def technology_id(self):
        """Generate a technology ID for testing."""
        return uuid.uuid4()
    
    def test_create_technology_ownership(self, db_session, game_id, owner_id, technology_id):
        """Test creating a technology ownership record."""
        # Create a technology ownership record
        ownership = TechnologyOwnership(
            game_id=game_id,
            owner_id=owner_id,
            technology_type="big_tech",
            technology_id=technology_id
        )
        
        db_session.add(ownership)
        db_session.commit()
        db_session.refresh(ownership)
        
        # Verify the technology ownership record was created
        assert ownership.id is not None
        assert ownership.game_id == game_id
        assert ownership.owner_id == owner_id
        assert ownership.technology_type == "big_tech"
        assert ownership.technology_id == technology_id
        assert isinstance(ownership.acquired_at, datetime)
    
    def test_unique_technology_ownership(self, db_session, game_id, owner_id, technology_id):
        """Test that a civilization can't own the same technology twice."""
        # Create a technology ownership record
        ownership1 = TechnologyOwnership(
            game_id=game_id,
            owner_id=owner_id,
            technology_type="big_tech",
            technology_id=technology_id
        )
        
        db_session.add(ownership1)
        db_session.commit()
        
        # Try to create another technology ownership record for the same owner and technology
        ownership2 = TechnologyOwnership(
            game_id=game_id,
            owner_id=owner_id,
            technology_type="big_tech",
            technology_id=technology_id
        )
        
        db_session.add(ownership2)
        
        # This should raise an integrity error due to the unique constraint
        with pytest.raises(IntegrityError):
            db_session.commit()

class TestProjectComponentAssignmentModel:
    """Tests for the ProjectComponentAssignment model."""
    
    @pytest.fixture
    def game_id(self, db_session):
        """Create a game and return its ID for testing."""
        from app.models.game import Game
        from app.schemas.enums import GameStatus
        
        game = Game(
            name="Test Game",
            status=GameStatus.SETUP,
            current_round=1
        )
        db_session.add(game)
        db_session.commit()
        db_session.refresh(game)
        return game.id

    @pytest.fixture
    def project_id(self, db_session, game_id):
        """Create a project development and return its ID for testing."""
        from app.models.technology import ProjectDevelopment
        from app.models.civilization import Civilization
        from app.schemas.enums import CivilizationName
        
        # Create a civilization
        civ = Civilization(
            game_id=game_id,
            name=CivilizationName.THRIZOTH,
            display_name="The Thrizoth"
        )
        db_session.add(civ)
        db_session.commit()
        
        # Create a project
        project = ProjectDevelopment(
            game_id=game_id,
            civilization_id=civ.id,
            project_type="universal",
            project_id=uuid.uuid4(),
            current_phase="research",
            progress_percentage=0.0
        )
        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)
        return project.id
    
    @pytest.fixture
    def component_id(self):
        """Generate a component ID for testing."""
        return uuid.uuid4()
    
    def test_create_component_assignment(self, db_session, game_id, project_id, component_id):
        """Test creating a component assignment."""
        # Create a component assignment
        assignment = ProjectComponentAssignment(
            game_id=game_id,
            project_id=project_id,
            component_id=component_id,
            component_type="big_tech"
        )
        
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)
        
        # Verify the component assignment was created
        assert assignment.id is not None
        assert assignment.game_id == game_id
        assert assignment.project_id == project_id
        assert assignment.component_id == component_id
        assert assignment.component_type == "big_tech"
        assert isinstance(assignment.assigned_at, datetime)
    
    def test_unique_component_assignment(self, db_session, game_id, component_id):
        """Test that a component can only be assigned to one project."""
        # Create civilizations for the projects
        from app.models.civilization import Civilization
        from app.schemas.enums import CivilizationName
        
        civ = Civilization(
            game_id=game_id,
            name=CivilizationName.THRIZOTH,
            display_name="The Thrizoth"
        )
        db_session.add(civ)
        db_session.commit()
        
        # Create two projects
        from app.models.technology import ProjectDevelopment
        
        project1 = ProjectDevelopment(
            game_id=game_id,
            civilization_id=civ.id,
            project_type="universal",
            project_id=uuid.uuid4(),
            current_phase="research",
            progress_percentage=0.0
        )
        
        project2 = ProjectDevelopment(
            game_id=game_id,
            civilization_id=civ.id,
            project_type="universal",
            project_id=uuid.uuid4(),
            current_phase="research",
            progress_percentage=0.0
        )
        
        db_session.add_all([project1, project2])
        db_session.commit()
        
        # Create a component assignment
        assignment1 = ProjectComponentAssignment(
            game_id=game_id,
            project_id=project1.id,
            component_id=component_id,
            component_type="big_tech"
        )
        
        db_session.add(assignment1)
        db_session.commit()
        
        # Try to create another component assignment for the same component
        assignment2 = ProjectComponentAssignment(
            game_id=game_id,
            project_id=project2.id,
            component_id=component_id,
            component_type="big_tech"
        )
        
        db_session.add(assignment2)
        
        # This should raise an integrity error due to the unique constraint
        with pytest.raises(IntegrityError):
            db_session.commit()