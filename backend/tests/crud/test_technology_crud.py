# File: tests/crud/test_technology_crud.py
import pytest
import uuid
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.crud import technology as crud_technology
from app.models.technology import (
    BigTechComponent, UberTechComponent, UniversalProject, 
    TechRequirement, ProjectDevelopment, TechnologyOwnership,
    ProjectComponentAssignment
)
from app.models.resource import ResourceType, Resource, CounterfeitResource
from app.schemas.technology import (
    ProjectDevelopmentCreate, ProjectComponentAssignmentCreate
)

class TestProjectDevelopmentCRUD:
    """Tests for ProjectDevelopment CRUD operations."""
    
    
    @pytest.fixture
    def game_id(self, db_session):
        """Create a game and return its ID for testing."""
        from app.models.game import Game
        
        # Create a game in the database
        game = Game(
            name="Test Tech Game",
            status="setup",
            current_round=1
        )
        db_session.add(game)
        db_session.commit()
        db_session.refresh(game)
        return game.id
    
    @pytest.fixture
    def civilization_id(self, db_session, game_id):
        """Generate a civilization ID for testing."""
        from app.models.civilization import Civilization
        
        civ = Civilization(
            id=uuid.uuid4(),
            game_id=game_id,
            name="Test Project Civilization",
            display_name="Test Project Civilization"
        )
        db_session.add(civ)
        db_session.commit()
        db_session.refresh(civ)
        return civ.id
    
    @pytest.fixture
    def project_id(self):
        """Generate a project ID for testing."""
        return uuid.uuid4()
    
    def test_start_project(self, db_session, game_id, civilization_id, project_id):
        """Test starting a new project development."""
        # Create project data
        project_data = ProjectDevelopmentCreate(
            game_id=game_id,
            civilization_id=civilization_id,
            project_type="universal",
            project_id=project_id
        )
        
        # Start the project
        project = crud_technology.start_project(db_session, project=project_data)
        
        # Verify the project was started
        assert project.id is not None
        assert project.game_id == game_id
        assert project.civilization_id == civilization_id
        assert project.project_type == "universal"
        assert project.project_id == project_id
        assert project.current_phase == "research"
        assert project.progress_percentage == 0.0
    
    def test_start_duplicate_project(self, db_session, game_id, civilization_id, project_id):
        """Test that starting the same project twice raises an error."""
        # Create project data
        project_data = ProjectDevelopmentCreate(
            game_id=game_id,
            civilization_id=civilization_id,
            project_type="universal",
            project_id=project_id
        )
        
        # Start the project
        crud_technology.start_project(db_session, project=project_data)
        
        # Try to start the same project again
        with pytest.raises(HTTPException) as excinfo:
            crud_technology.start_project(db_session, project=project_data)
        
        # Verify the error
        assert excinfo.value.status_code == 400
        assert "already in development" in excinfo.value.detail
    
    def test_get_project_development(self, db_session, game_id, civilization_id, project_id):
        """Test getting a project development by ID."""
        # Create project data
        project_data = ProjectDevelopmentCreate(
            game_id=game_id,
            civilization_id=civilization_id,
            project_type="universal",
            project_id=project_id
        )
        
        # Start the project
        started_project = crud_technology.start_project(db_session, project=project_data)
        
        # Get the project
        retrieved_project = crud_technology.get_project_development(db_session, project_id=started_project.id)
        
        # Verify the project was retrieved
        assert retrieved_project is not None
        assert retrieved_project.id == started_project.id
        assert retrieved_project.game_id == game_id
        assert retrieved_project.civilization_id == civilization_id
    
    def test_get_civilization_projects(self, db_session, game_id, civilization_id):
        """Test getting all projects being developed by a civilization."""
        # Create two projects
        project1_data = ProjectDevelopmentCreate(
            game_id=game_id,
            civilization_id=civilization_id,
            project_type="universal",
            project_id=uuid.uuid4()
        )
        
        project2_data = ProjectDevelopmentCreate(
            game_id=game_id,
            civilization_id=civilization_id,
            project_type="uber_tech",
            project_id=uuid.uuid4()
        )
        
        # Start the projects
        crud_technology.start_project(db_session, project=project1_data)
        crud_technology.start_project(db_session, project=project2_data)
        
        # Get the civilization's projects
        projects = crud_technology.get_civilization_projects(
            db_session,
            game_id=game_id,
            civilization_id=civilization_id
        )
        
        # Verify the projects were retrieved
        assert len(projects) == 2
        assert projects[0].civilization_id == civilization_id
        assert projects[1].civilization_id == civilization_id

class TestComponentAssignmentCRUD:
    """Tests for ProjectComponentAssignment CRUD operations."""
    
    @pytest.fixture
    def game_id(self, db_session):
        """Generate a game ID for testing."""
        from app.models.game import Game
        
        # Create a game in the database
        game = Game(
            name="Component Test Game",
            status="active",
            current_round=1
        )
        db_session.add(game)
        db_session.commit()
        db_session.refresh(game)
        return game.id
    
    @pytest.fixture
    def civilization_id(self, db_session, game_id):
        """Generate a civilization ID for testing."""
        from app.models.civilization import Civilization
        
        civ = Civilization(
            id=uuid.uuid4(),
            game_id=game_id,
            name="Test Civilization",
            display_name="Test Civilization"
        )
        db_session.add(civ)
        db_session.commit()
        db_session.refresh(civ)
        return civ.id
    
    @pytest.fixture
    def component_id(self):
        """Generate a component ID for testing."""
        return uuid.uuid4()
    
    @pytest.fixture
    def project(self, db_session, game_id, civilization_id):
        """Create a project for testing."""
        project_data = ProjectDevelopmentCreate(
            game_id=game_id,
            civilization_id=civilization_id,
            project_type="universal",
            project_id=uuid.uuid4()
        )
        
        return crud_technology.start_project(db_session, project=project_data)
    
    @pytest.fixture
    def technology_ownership(self, db_session, game_id, civilization_id, component_id):
        """Create a technology ownership record for testing."""
        from app.models.technology import TechnologyOwnership
        
        ownership = TechnologyOwnership(
            game_id=game_id,
            owner_id=civilization_id,
            technology_type="big_tech",
            technology_id=component_id
        )
        
        db_session.add(ownership)
        db_session.commit()
        db_session.refresh(ownership)
        return ownership
    
    def test_assign_component_to_project(
        self, db_session, game_id, civilization_id, component_id, project, technology_ownership
    ):
        """Test assigning a component to a project."""
        # Create assignment data
        assignment_data = ProjectComponentAssignmentCreate(
            game_id=game_id,
            project_id=project.id,
            component_id=component_id,
            component_type="big_tech"
        )
        
        # Assign the component
        assignment = crud_technology.assign_component_to_project(db_session, assignment=assignment_data)
        
        # Verify the component was assigned
        assert assignment.id is not None
        assert assignment.game_id == game_id
        assert assignment.project_id == project.id
        assert assignment.component_id == component_id
        assert assignment.component_type == "big_tech"
    
    def test_assign_nonexistent_component(self, db_session, game_id, project):
        """Test that assigning a nonexistent component raises an error."""
        # Create assignment data with a nonexistent component
        nonexistent_component_id = uuid.uuid4()
        assignment_data = ProjectComponentAssignmentCreate(
            game_id=game_id,
            project_id=project.id,
            component_id=nonexistent_component_id,
            component_type="big_tech"
        )
        
        # Try to assign the component
        with pytest.raises(HTTPException) as excinfo:
            crud_technology.assign_component_to_project(db_session, assignment=assignment_data)
        
        # Verify the error
        assert excinfo.value.status_code == 404
        assert "not found in civilization's inventory" in excinfo.value.detail
    
    def test_assign_already_assigned_component(
        self, db_session, game_id, civilization_id, component_id, project, technology_ownership
    ):
        """Test that assigning an already assigned component raises an error."""
        # Create assignment data
        assignment_data = ProjectComponentAssignmentCreate(
            game_id=game_id,
            project_id=project.id,
            component_id=component_id,
            component_type="big_tech"
        )
        
        # Assign the component
        crud_technology.assign_component_to_project(db_session, assignment=assignment_data)
        
        # Create another project
        project2_data = ProjectDevelopmentCreate(
            game_id=game_id,
            civilization_id=civilization_id,
            project_type="universal",
            project_id=uuid.uuid4()
        )
        
        project2 = crud_technology.start_project(db_session, project=project2_data)
        
        # Try to assign the same component to another project
        assignment_data2 = ProjectComponentAssignmentCreate(
            game_id=game_id,
            project_id=project2.id,
            component_id=component_id,
            component_type="big_tech"
        )
        
        with pytest.raises(HTTPException) as excinfo:
            crud_technology.assign_component_to_project(db_session, assignment=assignment_data2)
        
        # Verify the error
        assert excinfo.value.status_code == 400
        assert "already assigned to a project" in excinfo.value.detail
    
    def test_unassign_component(
        self, db_session, game_id, civilization_id, component_id, project, technology_ownership
    ):
        """Test removing a component assignment."""
        # Create assignment data
        assignment_data = ProjectComponentAssignmentCreate(
            game_id=game_id,
            project_id=project.id,
            component_id=component_id,
            component_type="big_tech"
        )
        
        # Assign the component
        assignment = crud_technology.assign_component_to_project(db_session, assignment=assignment_data)
        
        # Unassign the component
        result = crud_technology.unassign_component(db_session, assignment_id=assignment.id)
        
        # Verify the component was unassigned
        assert result["success"] is True
        
        # Verify the assignment no longer exists
        assignment_exists = db_session.query(ProjectComponentAssignment).filter(
            ProjectComponentAssignment.id == assignment.id
        ).first()
        
        assert assignment_exists is None

class TestBigTechAssemblyCRUD:
    """Tests for Big Tech assembly operations."""
    
    @pytest.fixture
    def game_id(self, db_session):
        """Generate a game ID for testing."""
        from app.models.game import Game
        
        game = Game(
            name="BigTech Test Game",
            status="active",
            current_round=1
        )
        db_session.add(game)
        db_session.commit()
        db_session.refresh(game)
        return game.id
    
    @pytest.fixture
    def civilization_id(self, db_session, game_id):
        """Generate a civilization ID for testing."""
        from app.models.civilization import Civilization
        
        civ = Civilization(
            id=uuid.uuid4(),
            game_id=game_id,
            name="Test BigTech Civilization",
            display_name="Test BigTech Civilization"
        )
        db_session.add(civ)
        db_session.commit()
        db_session.refresh(civ)
        return civ.id
    
    @pytest.fixture
    def resource_type(self, db_session):
        """Create a resource type for testing."""
        resource_type = ResourceType(
            name="Required Resource",
            category="Raw Material",
            rarity="Common"
        )
        
        db_session.add(resource_type)
        db_session.commit()
        db_session.refresh(resource_type)
        return resource_type
    
    @pytest.fixture
    def big_tech(self, db_session):
        """Create a Big Tech component for testing."""
        big_tech = BigTechComponent(
            name="Test Big Tech",
            tech_group="A"
        )
        
        db_session.add(big_tech)
        db_session.commit()
        db_session.refresh(big_tech)
        return big_tech
    
    @pytest.fixture
    def tech_requirement(self, db_session, big_tech, resource_type):
        """Create a tech requirement for testing."""
        requirement = TechRequirement(
            tech_type="big_tech",
            tech_id=big_tech.id,
            required_tech_type="resource",
            required_tech_id=resource_type.id,
            quantity=50
        )
        
        db_session.add(requirement)
        db_session.commit()
        db_session.refresh(requirement)
        return requirement
    
    def test_assemble_big_tech_with_sufficient_resources(
        self, db_session, game_id, civilization_id, big_tech, resource_type, tech_requirement
    ):
        """Test assembling a Big Tech component with sufficient resources."""
        # Add resources to the civilization's inventory
        resource = Resource(
            game_id=game_id,
            owner_id=civilization_id,
            resource_type_id=resource_type.id,
            quantity=100
        )
        
        db_session.add(resource)
        db_session.commit()
        
        # Assemble the Big Tech component
        result = crud_technology.assemble_big_tech(
            db_session,
            game_id=game_id,
            civilization_id=civilization_id,
            big_tech_id=big_tech.id
        )
        
        # Verify the Big Tech component was assembled
        assert result["success"] is True
        
        # Verify the resources were consumed
        updated_resource = db_session.query(Resource).filter(
            Resource.game_id == game_id,
            Resource.owner_id == civilization_id,
            Resource.resource_type_id == resource_type.id
        ).first()
        
        assert updated_resource.quantity == 50
        
        # Verify the Big Tech component was added to the civilization's inventory
        tech_ownership = db_session.query(TechnologyOwnership).filter(
            TechnologyOwnership.game_id == game_id,
            TechnologyOwnership.owner_id == civilization_id,
            TechnologyOwnership.technology_id == big_tech.id,
            TechnologyOwnership.technology_type == "big_tech"
        ).first()
        
        assert tech_ownership is not None
    
    def test_assemble_big_tech_with_insufficient_resources(
        self, db_session, game_id, civilization_id, big_tech, resource_type, tech_requirement
    ):
        """Test that assembling a Big Tech component with insufficient resources fails."""
        # Add insufficient resources to the civilization's inventory
        resource = Resource(
            game_id=game_id,
            owner_id=civilization_id,
            resource_type_id=resource_type.id,
            quantity=30
        )
        
        db_session.add(resource)
        db_session.commit()
        
        # Try to assemble the Big Tech component
        result = crud_technology.assemble_big_tech(
            db_session,
            game_id=game_id,
            civilization_id=civilization_id,
            big_tech_id=big_tech.id
        )
        
        # Verify the assembly failed
        assert result["success"] is False
        assert result["error"] == "insufficient_resources"
        
        # Verify the resources were not consumed
        updated_resource = db_session.query(Resource).filter(
            Resource.game_id == game_id,
            Resource.owner_id == civilization_id,
            Resource.resource_type_id == resource_type.id
        ).first()
        
        assert updated_resource.quantity == 30
    
    def test_assemble_big_tech_with_counterfeit_resources(
        self, db_session, game_id, civilization_id, big_tech, resource_type, tech_requirement
    ):
        """Test that assembling a Big Tech component with counterfeit resources fails."""
        # Add resources to the civilization's inventory
        resource = Resource(
            game_id=game_id,
            owner_id=civilization_id,
            resource_type_id=resource_type.id,
            quantity=100
        )
        
        # Add counterfeit resources as well
        counterfeit = CounterfeitResource(
            game_id=game_id,
            owner_id=civilization_id,
            resource_type_id=resource_type.id,
            quantity=50,
            batch_id="fake_batch_1"
        )
        
        db_session.add_all([resource, counterfeit])
        db_session.commit()
        
        # Try to assemble the Big Tech component
        result = crud_technology.assemble_big_tech(
            db_session,
            game_id=game_id,
            civilization_id=civilization_id,
            big_tech_id=big_tech.id
        )
        
        # Verify the assembly failed
        assert result["success"] is False
        assert result["error"] == "counterfeit_detected"
        
        # Verify the resources were not consumed
        updated_resource = db_session.query(Resource).filter(
            Resource.game_id == game_id,
            Resource.owner_id == civilization_id,
            Resource.resource_type_id == resource_type.id
        ).first()
        
        assert updated_resource.quantity == 100
    
    def test_destroy_counterfeit_resource(self, db_session, game_id, civilization_id, resource_type):
        """Test destroying a counterfeit resource batch."""
        # Create a counterfeit resource
        counterfeit = CounterfeitResource(
            game_id=game_id,
            owner_id=civilization_id,
            resource_type_id=resource_type.id,
            quantity=50,
            batch_id="fake_batch_to_destroy"
        )
        
        db_session.add(counterfeit)
        db_session.commit()
        
        # Destroy the counterfeit resource
        result = crud_technology.destroy_counterfeit_resource(
            db_session,
            game_id=game_id,
            civilization_id=civilization_id,
            batch_id="fake_batch_to_destroy"
        )
        
        # Verify the counterfeit resource was destroyed
        assert result["success"] is True
        assert result["resource_type_id"] == str(resource_type.id)
        assert result["quantity_destroyed"] == 50
        
        # Verify the counterfeit resource no longer exists
        counterfeit_exists = db_session.query(CounterfeitResource).filter(
            CounterfeitResource.game_id == game_id,
            CounterfeitResource.owner_id == civilization_id,
            CounterfeitResource.batch_id == "fake_batch_to_destroy"
        ).first()
        
        assert counterfeit_exists is None

class TestProjectAssemblyCRUD:
    """Tests for project assembly operations."""
    
    @pytest.fixture
    def game_id(self, db_session):
        """Generate a game ID for testing."""
        from app.models.game import Game
        
        game = Game(
            name="Assembly Test Game",
            status="active",
            current_round=1
        )
        db_session.add(game)
        db_session.commit()
        db_session.refresh(game)
        return game.id
    
    @pytest.fixture
    def civilization_id(self, db_session, game_id):
        """Generate a civilization ID for testing."""
        from app.models.civilization import Civilization
        
        civ = Civilization(
            id=uuid.uuid4(),
            game_id=game_id,
            name="Test Assembly Civilization",
            display_name="Test Assembly Civilization"
        )
        db_session.add(civ)
        db_session.commit()
        db_session.refresh(civ)
        return civ.id
    
    @pytest.fixture
    def tech_component_id(self):
        """Generate a technology component ID for testing."""
        return uuid.uuid4()
    
    @pytest.fixture
    def project_template_id(self):
        """Generate a project template ID for testing."""
        return uuid.uuid4()
    
    @pytest.fixture
    def project(self, db_session, game_id, civilization_id, project_template_id):
        """Create a project for testing."""
        project_data = ProjectDevelopmentCreate(
            game_id=game_id,
            civilization_id=civilization_id,
            project_type="universal",
            project_id=project_template_id
        )
        
        return crud_technology.start_project(db_session, project=project_data)
    
    @pytest.fixture
    def tech_requirement(self, db_session, project_template_id, tech_component_id):
        """Create a tech requirement for testing."""
        requirement = TechRequirement(
            tech_type="universal",
            tech_id=project_template_id,
            required_tech_type="uber_tech",
            required_tech_id=tech_component_id,
            quantity=1
        )
        
        db_session.add(requirement)
        db_session.commit()
        db_session.refresh(requirement)
        return requirement
    
    @pytest.fixture
    def technology_ownership(self, db_session, game_id, civilization_id, tech_component_id):
        """Create a technology ownership record for testing."""
        ownership = TechnologyOwnership(
            game_id=game_id,
            owner_id=civilization_id,
            technology_type="uber_tech",
            technology_id=tech_component_id
        )
        
        db_session.add(ownership)
        db_session.commit()
        db_session.refresh(ownership)
        return ownership
    
    @pytest.fixture
    def component_assignment(
        self, db_session, game_id, project, tech_component_id, technology_ownership
    ):
        """Create a component assignment for testing."""
        assignment = ProjectComponentAssignment(
            game_id=game_id,
            project_id=project.id,
            component_id=tech_component_id,
            component_type="uber_tech"
        )
        
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)
        return assignment
    
    def test_assemble_project_with_all_components(
        self, db_session, game_id, project, component_assignment, tech_requirement
    ):
        """Test assembling a project with all required components."""
        # Assemble the project
        result = crud_technology.assemble_project(
            db_session,
            game_id=game_id,
            project_id=project.id
        )
        
        # Verify the project was assembled
        assert result["success"] is True
        
        # Verify the project is marked as complete
        completed_project = crud_technology.get_project_development(db_session, project_id=project.id)
        assert completed_project.progress_percentage == 100.0
        assert completed_project.completed_at is not None
        
        # Verify the component assignment no longer exists
        assignment_exists = db_session.query(ProjectComponentAssignment).filter(
            ProjectComponentAssignment.id == component_assignment.id
        ).first()
        
        assert assignment_exists is None
        
        # Verify the technology was added to the civilization's inventory
        tech_ownership = db_session.query(TechnologyOwnership).filter(
            TechnologyOwnership.game_id == game_id,
            TechnologyOwnership.owner_id == project.civilization_id,
            TechnologyOwnership.technology_id == project.project_id,
            TechnologyOwnership.technology_type == project.project_type
        ).first()
        
        assert tech_ownership is not None
    
    def test_assemble_project_with_missing_components(
        self, db_session, game_id, project, tech_requirement
    ):
        """Test that assembling a project with missing components fails."""
        # Try to assemble the project without assigning the required component
        result = crud_technology.assemble_project(
            db_session,
            game_id=game_id,
            project_id=project.id
        )
        
        # Verify the assembly failed
        assert result["success"] is False
        assert result["error"] == "incomplete"
        
        # Verify the project is not marked as complete
        incomplete_project = crud_technology.get_project_development(db_session, project_id=project.id)
        assert incomplete_project.progress_percentage < 100.0
        assert incomplete_project.completed_at is None