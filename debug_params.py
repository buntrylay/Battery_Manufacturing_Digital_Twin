"""
Debug script to test parameter mapping
"""
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from server.parameter_mapper import ParameterMapper

# Test coating parameters
test_frontend_data = {
    "Coating Speed": "0.05",
    "Gap Height": "200e-6", 
    "Flow Rate": "5e-6",
    "Coating Width": "0.5"
}

print("=== PARAMETER MAPPING DEBUG ===")
print(f"Test frontend data: {test_frontend_data}")

try:
    # Test stage to machine info
    line_type, machine_id = ParameterMapper.stage_to_machine_info("Anode Coating")
    print(f"Stage 'Anode Coating' -> line_type: {line_type}, machine_id: {machine_id}")
    
    # Test frontend to backend parameter conversion
    backend_params = ParameterMapper.frontend_to_backend_parameters(test_frontend_data, machine_id)
    print(f"Backend parameters: {backend_params}")
    
    # Test parameter object creation
    param_obj = ParameterMapper.create_parameter_object(backend_params, machine_id)
    print(f"Parameter object created: {param_obj}")
    print("✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()