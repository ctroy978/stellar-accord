# tests/config/test_debug.py
from app.config.star_map import StarMapConfig

def test_debug_star_map_defaults():
    """Debug test to examine default StarMapConfig."""
    config = StarMapConfig()
    
    # Print out systems and connections
    print("\nDEBUG OUTPUT:")
    print("-------------")
    print(f"Number of systems: {len(config.systems)}")
    for system_id, system in config.systems.items():
        print(f"System: {system_id}, Position: {system.position}, Civilization: {system.civilization_id}")
    
    print("\nConnections:")
    for system_id, connected_ids in config.connections.items():
        print(f"{system_id} -> {connected_ids}")
    
    # Check what connections might be invalid
    for system_id, connected_ids in config.connections.items():
        if system_id not in config.systems:
            print(f"ERROR: System {system_id} in connections doesn't exist")
        for connected_id in connected_ids:
            if connected_id not in config.systems:
                print(f"ERROR: Connected system {connected_id} from {system_id} doesn't exist")
    
    # This test is just for debugging, no assertions
    assert True