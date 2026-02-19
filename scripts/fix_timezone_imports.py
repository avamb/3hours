#!/usr/bin/env python3
"""
Fix missing timezone imports in models after update_models_for_timestamptz.py
"""

import os
import re
from pathlib import Path


def fix_timezone_import(filepath):
    """Fix missing timezone import in a file"""

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if file uses timezone.utc
    if 'timezone.utc' not in content:
        return False

    # Check if timezone is already imported
    if re.search(r'from datetime import.*timezone', content):
        print(f"  - {filepath.name} already has timezone import")
        return False

    # Find the datetime import line
    import_match = re.search(r'from datetime import ([^\n]+)', content)
    if import_match:
        imports = import_match.group(1)
        # Add timezone to imports if not already there
        if 'timezone' not in imports:
            new_imports = imports.rstrip() + ', timezone'
            content = content.replace(
                f'from datetime import {imports}',
                f'from datetime import {new_imports}'
            )

            # Write the fixed content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"  [FIXED] {filepath.name}")
            return True

    return False


def main():
    """Main function"""

    print("=" * 60)
    print("FIXING MISSING TIMEZONE IMPORTS")
    print("=" * 60)
    print()

    models_dir = Path('src/db/models')
    model_files = list(models_dir.glob('*.py'))

    fixed_count = 0
    for filepath in model_files:
        if filepath.name != '__init__.py':
            if fix_timezone_import(filepath):
                fixed_count += 1

    print()
    print(f"Fixed {fixed_count} files")

    if fixed_count > 0:
        print()
        print("=" * 60)
        print("FIXES COMPLETE!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Review the changes")
        print("2. Rebuild Docker image")
        print("3. Redeploy to production")


if __name__ == "__main__":
    main()