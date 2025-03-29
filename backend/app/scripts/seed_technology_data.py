# file: app/scripts/seed_technology_data.py
import uuid
from sqlalchemy.orm import Session
from app.models.technology import (
    BigTechComponent, UberTechComponent, UniversalProject, TechRequirement
)
from app.db.session import SessionLocal

def seed_universal_projects():
    db = SessionLocal()
    try:
        # Example of adding one Universal Project
        dyson_sphere = UniversalProject(
            id=uuid.uuid4(),
            name="Dyson Sphere",
            description="A megastructure surrounding a star to capture nearly 100% of its energy output.",
            beneficiaries=["Silicon Liberation", "Voidborn Nomads"],
            harmed=["Arborealis Nexus", "Glacian Current"]
        )
        
        db.add(dyson_sphere)
        db.commit()
        
        # Add the Uber-Tech requirements for this project
        for required_uber_tech in [
            "Energy Manipulation Matrix", 
            "Structural Integrity Field", 
            "Thermal Regulation Network", 
            "Stellar Manipulation Array"
        ]:
            # Look up the Uber-Tech ID (assuming it exists)
            uber_tech = db.query(UberTechComponent).filter(
                UberTechComponent.name == required_uber_tech
            ).first()
            
            if uber_tech:
                requirement = TechRequirement(
                    tech_type="universal",
                    tech_id=dyson_sphere.id,
                    required_tech_type="uber_tech",
                    required_tech_id=uber_tech.id
                )
                db.add(requirement)
        
        db.commit()
        
        # Repeat for other Universal Projects...
    
    finally:
        db.close()

def seed_uber_tech_components():
    db = SessionLocal()
    try:
        # Example of adding one Uber-Tech Component
        energy_matrix = UberTechComponent(
            id=uuid.uuid4(),
            name="Energy Manipulation Matrix",
            description="Fundamental system for controlling and transforming energy"
        )
        
        db.add(energy_matrix)
        db.commit()
        
        # Add the Big Tech requirements for this Uber-Tech
        for required_big_tech in [
            "Power Conversion System",
            "Energy Amplification Array",
            "Directional Flow Controller",
            "Containment Field Generator",
            "Wave Harmonization Grid",
            "Quantum Calculation Engine"
        ]:
            # Look up the Big Tech ID (assuming it exists)
            big_tech = db.query(BigTechComponent).filter(
                BigTechComponent.name == required_big_tech
            ).first()
            
            if big_tech:
                requirement = TechRequirement(
                    tech_type="uber_tech",
                    tech_id=energy_matrix.id,
                    required_tech_type="big_tech",
                    required_tech_id=big_tech.id
                )
                db.add(requirement)
        
        db.commit()
        
        # Repeat for other Uber-Tech Components...
    
    finally:
        db.close()

def seed_big_tech_components():
    db = SessionLocal()
    try:
        # Example of adding one Big Tech Component
        power_conversion = BigTechComponent(
            id=uuid.uuid4(),
            name="Power Conversion System",
            description="System for efficiently converting energy between different forms",
            tech_group="A"
        )
        
        db.add(power_conversion)
        db.commit()
        
        # Add the Resource requirements for this Big Tech
        resource_requirements = [
            {"name": "Neutronium", "quantity": 30},
            {"name": "Photon Crystal", "quantity": 25},
            {"name": "Living Metal", "quantity": 15}
        ]
        
        for req in resource_requirements:
            # Look up the Resource Type ID (assuming it exists)
            from app.models.resource import ResourceType
            resource_type = db.query(ResourceType).filter(
                ResourceType.name == req["name"]
            ).first()
            
            if resource_type:
                requirement = TechRequirement(
                    tech_type="big_tech",
                    tech_id=power_conversion.id,
                    required_tech_type="resource",
                    required_tech_id=resource_type.id,
                    quantity=req["quantity"]
                )
                db.add(requirement)
        
        db.commit()
        
        # Repeat for other Big Tech Components...
    
    finally:
        db.close()

def run_seed():
    # Run in the correct order to handle dependencies
    seed_big_tech_components()
    seed_uber_tech_components()
    seed_universal_projects()

if __name__ == "__main__":
    run_seed()