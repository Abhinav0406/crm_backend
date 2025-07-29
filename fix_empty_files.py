#!/usr/bin/env python
"""
Script to add content to empty __init__.py files.
"""

import os

def fix_empty_files():
    """Add content to empty __init__.py files."""
    empty_files = [
        'apps/analytics/__init__.py',
        'apps/automation/__init__.py',
        'apps/clients/__init__.py',
        'apps/integrations/__init__.py',
        'apps/products/__init__.py',
        'apps/sales/__init__.py',
        'apps/tenants/__init__.py',
        'apps/users/__init__.py',
        'shared/__init__.py',
    ]
    
    for file_path in empty_files:
        if os.path.exists(file_path) and os.path.getsize(file_path) == 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('# Package\n')
            print(f"Fixed: {file_path}")

if __name__ == '__main__':
    fix_empty_files() 