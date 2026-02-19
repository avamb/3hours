#!/usr/bin/env python3
"""
Script to update all SQLAlchemy models to use DateTime(timezone=True)
Run this AFTER the migration is applied and verified
"""

import os
import re
from pathlib import Path


def update_datetime_imports(content):
    """Update imports to use timezone-aware DateTime"""

    # Pattern to find DateTime imports
    import_pattern = r'from sqlalchemy import ([^)]*?)DateTime'

    def replace_import(match):
        imports = match.group(1)
        # Check if we already have the timezone import
        if 'DateTime' not in imports:
            return match.group(0)
        return f'from sqlalchemy import {imports}DateTime'

    content = re.sub(import_pattern, replace_import, content)

    return content


def update_datetime_columns(content):
    """Update DateTime column definitions to use timezone=True"""

    # Pattern 1: mapped_column(DateTime, ...)
    pattern1 = r'mapped_column\(DateTime(?!\()'

    content = re.sub(
        pattern1,
        'mapped_column(DateTime(timezone=True)',
        content
    )

    # Pattern 2: Column(DateTime, ...)
    pattern2 = r'Column\(DateTime(?!\()'

    content = re.sub(
        pattern2,
        'Column(DateTime(timezone=True)',
        content
    )

    return content


def remove_tzinfo_replacements(content):
    """Remove all .replace(tzinfo=None) calls"""

    # Pattern to match .replace(tzinfo=None)
    pattern = r'\.replace\(tzinfo=None\)'

    content = re.sub(pattern, '', content)

    return content


def update_default_values(content):
    """Update default datetime values to use timezone-aware datetime"""

    # Pattern for datetime.utcnow
    pattern1 = r'datetime\.utcnow(?:\(\))?'
    content = re.sub(pattern1, 'lambda: datetime.now(timezone.utc)', content)

    # Pattern for datetime.now(timezone.utc).replace(tzinfo=None)
    pattern2 = r'datetime\.now\(timezone\.utc\)\.replace\(tzinfo=None\)'
    content = re.sub(pattern2, 'datetime.now(timezone.utc)', content)

    # Add timezone import if datetime.now(timezone.utc) is used
    if 'datetime.now(timezone.utc)' in content and 'from datetime import' in content:
        # Check if timezone is already imported
        if 'timezone' not in content:
            # Find the datetime import line
            import_match = re.search(r'from datetime import ([^\n]+)', content)
            if import_match:
                imports = import_match.group(1)
                if 'timezone' not in imports:
                    new_imports = imports.rstrip() + ', timezone'
                    content = content.replace(
                        f'from datetime import {imports}',
                        f'from datetime import {new_imports}'
                    )

    return content


def process_model_file(filepath):
    """Process a single model file"""

    print(f"Processing {filepath.name}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Apply transformations
    content = update_datetime_imports(content)
    content = update_datetime_columns(content)
    content = remove_tzinfo_replacements(content)
    content = update_default_values(content)

    if content != original_content:
        # Create backup
        backup_path = filepath.with_suffix('.py.bak')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)

        # Write updated content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  [OK] Updated {filepath.name} (backup: {backup_path.name})")
        return True
    else:
        print(f"  - No changes needed in {filepath.name}")
        return False


def process_service_file(filepath):
    """Process a service file to remove tzinfo replacements"""

    print(f"Processing {filepath.name}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Remove .replace(tzinfo=None)
    content = remove_tzinfo_replacements(content)

    # Update any datetime.now(timezone.utc).replace(tzinfo=None)
    pattern = r'datetime\.now\(timezone\.utc\)\.replace\(tzinfo=None\)'
    content = re.sub(pattern, 'datetime.now(timezone.utc)', content)

    if content != original_content:
        # Create backup
        backup_path = filepath.with_suffix('.py.bak')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)

        # Write updated content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  [OK] Updated {filepath.name} (backup: {backup_path.name})")
        return True
    else:
        print(f"  - No changes needed in {filepath.name}")
        return False


def main():
    """Main function"""

    print("=" * 60)
    print("UPDATING MODELS FOR TIMESTAMPTZ")
    print("=" * 60)
    print()

    # Update model files
    print("Updating SQLAlchemy models:")
    print("-" * 60)

    models_dir = Path('src/db/models')
    model_files = list(models_dir.glob('*.py'))

    models_updated = 0
    for filepath in model_files:
        if filepath.name != '__init__.py':
            if process_model_file(filepath):
                models_updated += 1

    print()
    print(f"Updated {models_updated} model files")

    # Update service files
    print()
    print("Updating service files:")
    print("-" * 60)

    services_dir = Path('src/services')
    service_files = list(services_dir.glob('*.py'))

    # Also update handlers
    handlers_dir = Path('src/bot/handlers')
    handler_files = list(handlers_dir.glob('*.py'))

    services_updated = 0
    for filepath in service_files + handler_files:
        if filepath.name != '__init__.py':
            if process_service_file(filepath):
                services_updated += 1

    print()
    print(f"Updated {services_updated} service/handler files")

    print()
    print("=" * 60)
    print("UPDATE COMPLETE!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Review the changes")
    print("2. Run tests to ensure everything works")
    print("3. Delete backup files (*.bak) after verification")
    print()
    print("To restore original files if needed:")
    print("  for f in src/**/*.py.bak; do mv $f ${f%.bak}; done")


if __name__ == "__main__":
    main()