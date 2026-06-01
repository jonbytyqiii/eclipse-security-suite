#!/usr/bin/env python3
import os
import sys

def main():
    # Dynamically locate the home directory of the Apex module
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    sys.path.insert(0, base_dir)
    
    # Import your pristine listener module
    import listener
    audit_node = listener.ApexListener()
    
    # Dynamically check for the correct server instantiation method name
    if hasattr(audit_node, 'start'):
        audit_node.start()
    elif hasattr(audit_node, 'listen'):
        audit_node.listen()
    elif hasattr(audit_node, 'open_port'):
        audit_node.open_port()
    else:
        # Fallback to display the methods if there's an unexpected name structure
        available_methods = [m for m in dir(audit_node) if not m.startswith('_')]
        print(f"[!] Error: Could not find matching execution loop. Available methods: {available_methods}")

if __name__ == '__main__':
    main()