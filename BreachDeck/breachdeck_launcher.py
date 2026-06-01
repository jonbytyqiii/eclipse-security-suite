#!/usr/bin/env python3
import os
import sys

def main():
    # Dynamically track the home directory of the BreachDeck suite
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    sys.path.insert(0, base_dir)
    
    # Import your pristine interceptor script components safely
    import interceptor
    
    if hasattr(interceptor, 'main'):
        interceptor.main()
    elif hasattr(interceptor, 'start_interceptor'):
        interceptor.start_interceptor()
    elif hasattr(interceptor, 'run'):
        interceptor.run()
    else:
        # Resolve the absolute path of the interceptor script file
        target_file = os.path.join(base_dir, "interceptor.py")
        
        with open(target_file, "r", encoding="utf-8") as f:
            code = f.read()
            
        # Execute the script text while fully preserving __file__ and environment namespaces
        global_context = {
            "__name__": "__main__",
            "__file__": target_file
        }
        exec(code, global_context)

if __name__ == '__main__':
    main()