import subprocess
import sys
import os

def main():
    """
    Runs all SQLite initialization scripts.
    This script executes each init script within the 'sqlite' directory
    (its own location) to resolve local imports correctly. This allows
    the script to be run from any directory.
    """
    # Determine project directories to correctly resolve modules and paths
    sqlite_dir = os.path.dirname(os.path.abspath(__file__))
    unified_dir = os.path.dirname(sqlite_dir)
    project_root = os.path.dirname(unified_dir) # Assumes 'Unified' is one level down from root

    # Convert script paths to module paths to be run with `python -m`
    # These module paths are relative to the project root (e.g., 'Connectors-Ann')
    script_modules = [
        "Unified.sqlite.init.applications",
        "Unified.sqlite.init.databases",
        "Unified.sqlite.init.devops_and_iot",
        "Unified.sqlite.init.ecommerce",
        "Unified.sqlite.init.spreadsheet",
    ]

    print("Initializing SQLite database...")
    print("This will create 'wwwsmart_credentials.db' inside the 'sqlite/' directory.")

    for module_name in script_modules:
        print(f"\n--- Running {module_name.split('.')[-1]}.py ---") # e.g. applications.py
        try:
            # Execute `python -m Unified.sqlite.init.script` from the project root
            result = subprocess.run(
                [sys.executable, "-m", module_name],
                check=True,
                capture_output=True,
                text=True,
                cwd=project_root  # Set the working directory to the project root
            )
            print(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running {module_name}:", file=sys.stderr)
            print(e.stderr, file=sys.stderr)
            sys.exit(1)

    print("\n✅ Database initialization complete.")

if __name__ == "__main__":
    main()