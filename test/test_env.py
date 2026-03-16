import sys
import os

def verify():
    print(f"Python Executable: {sys.executable}")
    print(f"Virtual Env: {os.getenv('VIRTUAL_ENV', 'None')}")
    
    try:
        import pydantic
        print(f"[PASS] Pydantic found! Version: {pydantic.__version__}")
        print("Your environment is correctly configured.")
    except ImportError:
        print("[FAIL] Pydantic NOT found in this environment.")
        print("\nTo fix this in VS Code:")
        print("1. Press Ctrl+Shift+P")
        print("2. Type 'Python: Select Interpreter'")
        print("3. Choose the one pointing to '.venv\\Scripts\\python.exe'")

if __name__ == "__main__":
    verify()
