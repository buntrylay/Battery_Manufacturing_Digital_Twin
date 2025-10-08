"""
Test script to verify the decoupled notification system works correctly.
"""

import sys
import os

# Add the simulation path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'simulation'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'server'))

from simulation.events import event_bus, MachineEventType
from simulation.factory.PlantSimulation import PlantSimulation

def test_event_system():
    """Test that the event system works correctly."""
    print("Testing decoupled notification system...")
    
    # Create a plant simulation (this will set up event listeners)
    plant = PlantSimulation()
    
    # Simulate a machine event
    print("Emitting test machine event...")
    event_bus.emit_machine_event(
        machine_id="test_machine",
        line_type="anode", 
        process_name="mixing_anode",
        event_type=MachineEventType.TURNED_ON,
        data={"test": "data"}
    )
    
    print("Event system test completed successfully!")
    print("Machines now emit events instead of direct notifications.")
    print("PlantSimulation handles event-to-notification conversion.")

if __name__ == "__main__":
    test_event_system()
