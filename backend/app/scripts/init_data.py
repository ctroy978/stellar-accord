# File: app/scripts/init_data.py
import sys
import os
from pathlib import Path

# Add the parent directory to sys.path to allow imports from app
parent_dir = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(parent_dir)

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.schemas.resource import ResourceTypeCreate
from app.crud import resource as crud_resource
from app.schemas.enums import ResourceCategory, ResourceRarity

def init_resource_types():
    """Initialize the database with sample resource types."""
    db = SessionLocal()
    try:
        # Define sample resource types
        sample_resources = [
            ResourceTypeCreate(
                name="Neutronium",
                category=ResourceCategory.RAW_MATERIAL,
                rarity=ResourceRarity.RARE,
                description="A rare material with exceptional density and energy storage properties.",
                producible_by=["Thrizoth", "Silicon Liberation"]
            ),
            ResourceTypeCreate(
                name="Solar Essence",
                category=ResourceCategory.ENERGY_SOURCE,
                rarity=ResourceRarity.COMMON,
                description="Captures and stores solar energy in a compact crystalline structure.",
                producible_by=["Thrizoth", "Kyrathi", "Vasku"]
            ),
            ResourceTypeCreate(
                name="Quantum Particles",
                category=ResourceCategory.RAW_MATERIAL,
                rarity=ResourceRarity.UNCOMMON,
                description="Subatomic particles that exist in multiple quantum states simultaneously.",
                producible_by=["Silicon Liberation", "Vasku", "Methane Collective"]
            ),
            ResourceTypeCreate(
                name="Crystal Resonance",
                category=ResourceCategory.TECHNOLOGY,
                rarity=ResourceRarity.RARE,
                description="Harmonically aligned crystal structures that can amplify and direct energy.",
                producible_by=["Kyrathi", "Glacian Current"]
            ),
            ResourceTypeCreate(
                name="Atmospheric Nexus",
                category=ResourceCategory.REFINED_MATERIAL,
                rarity=ResourceRarity.UNCOMMON,
                description="A processed gas compound that regulates atmospheric conditions.",
                producible_by=["Methane Collective", "Glacian Current"]
            ),
        ]
        
        # Add each resource type to the database
        for resource in sample_resources:
            try:
                crud_resource.create_resource_type(db, resource)
                print(f"Created resource type: {resource.name}")
            except Exception as e:
                print(f"Error creating {resource.name}: {str(e)}")
                
        print("Sample resource types initialized successfully!")
        
    finally:
        db.close()

if __name__ == "__main__":
    init_resource_types()