import sys
import os
import importlib

print("=" * 50)
print("IMPORT DIAGNOSTIC TOOL")
print("=" * 50)

print(f"Python executable: {sys.executable}")
print(f"Current working directory: {os.getcwd()}")
print(f"Script location: {__file__}")
print("\nPython path:")
for i, path in enumerate(sys.path):
    print(f"  {i}: {path}")

print("\nFiles in current directory:")
for file in os.listdir('.'):
    print(f"  - {file}")

print("\n" + "=" * 50)
print("Attempting to import seed_data...")
print("=" * 50)

# Method 1: Direct import
try:
    import seed_data
    print("✓ Method 1: 'import seed_data' succeeded")
    print(f"  seed_data location: {seed_data.__file__}")
    print(f"  seed_data attributes: {dir(seed_data)}")
except ImportError as e:
    print(f"✗ Method 1 failed: {e}")

# Method 2: From import
try:
    from seed_data import main
    print("✓ Method 2: 'from seed_data import main' succeeded")
    print(f"  main function: {main}")
except ImportError as e:
    print(f"✗ Method 2 failed: {e}")

# Method 3: Importlib
try:
    spec = importlib.util.find_spec("seed_data")
    if spec:
        print(f"✓ Method 3: Found seed_data at {spec.origin}")
        module = importlib.import_module("seed_data")
        print(f"  Module loaded: {module}")
        if hasattr(module, 'main'):
            print("  ✓ module has main() function")
        else:
            print("  ✗ module has NO main() function")
    else:
        print("✗ Method 3: seed_data not found by importlib")
except Exception as e:
    print(f"✗ Method 3 error: {e}")

# Method 4: Check if there's a syntax error in seed_data.py
print("\n" + "=" * 50)
print("Checking seed_data.py for syntax errors...")
print("=" * 50)

try:
    with open('seed_data.py', 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"File size: {len(content)} bytes")
        print("First 200 characters:")
        print(content[:200])
        
    # Try to compile it
    compile(content, 'seed_data.py', 'exec')
    print("✓ No syntax errors in seed_data.py")
    
except SyntaxError as e:
    print(f"✗ Syntax error in seed_data.py: {e}")
    print(f"  Line {e.lineno}: {e.text}")
except Exception as e:
    print(f"✗ Error reading seed_data.py: {e}")

print("\n" + "=" * 50)
print("DIAGNOSTIC COMPLETE")
print("=" * 50)