import os
import sys
import traceback

print("Starting debug script...")
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# Add src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
print(f"Adding to path: {src_path}")
sys.path.insert(0, src_path)

try:
    print("Attempting to import BB84Analysis...")
    from analysis import BB84Analysis
    print("Successfully imported BB84Analysis")
    
    print("Attempting to import BB84Protocol...")
    from bb84_protocol import BB84Protocol
    print("Successfully imported BB84Protocol")
    
    print("Creating BB84Analysis instance...")
    analyzer = BB84Analysis(n_bits=100, n_trials=5)  # Smaller values for testing
    print("Successfully created analyzer")
    
    print("Running quick test...")
    protocol = BB84Protocol(n_bits=50)
    result = protocol.run_protocol(with_eve=False)
    print(f"Test result: {result}")
    
except Exception as e:
    print(f"Error occurred: {type(e).__name__}: {e}")
    print("Full traceback:")
    traceback.print_exc()