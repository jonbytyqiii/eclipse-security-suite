#!/usr/bin/env python3
import os
import sys

def main():
    # Dynamically locate the home directory of the Dexter module
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    sys.path.insert(0, base_dir)
    
    # Import your pristine dexter engine safely
    import dexter
    
    # Check for a standard main/run structure, otherwise safely execute the flat code text
    if hasattr(dexter, 'main'):
        dexter.main()
    elif hasattr(dexter, 'run'):
        dexter.run()
    else:
        target_file = os.path.join(base_dir, "dexter.py")
        with open(target_file, "r", encoding="utf-8") as f:
            code = f.read()
            
        # Execute while explicitly injecting namespaces to support internal relative file paths
        global_context = {
            "__name__": "__main__",
            "__file__": target_file
        }
        exec(code, global_context)

if __name__ == '__main__':
    main()