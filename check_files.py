import os
from pathlib import Path

def check_project_structure():
    root_dir = Path.cwd()
    
    for path in sorted(Path(root_dir).rglob('*')):
        if path.is_file():
            relative_path = path.relative_to(root_dir)
            print(f"✓ {relative_path}")
            
        if path.is_dir():
            relative_path = path.relative_to(root_dir)
            print(f"\n📁 {relative_path}")

if __name__ == "__main__":
    check_project_structure()