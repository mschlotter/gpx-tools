"""GPX_IO handles GPX file IO.
"""

import filecmp
import yaml
import os
import shutil

def load_config(config_path):
    """Load configuration from YAML file with error handling.
    
    Searches for the config file in:
    1. The provided path (if absolute or relative to current directory)
    2. config/ directory relative to the project root
    3. config/ directory relative to this module's location
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        dict: Configuration dictionary or None if not found
    """
    # Try the provided path first
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    # Get the project root (grandparent of this module's directory)
    module_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(module_dir))
    
    # Try config/ directory relative to project root
    config_path_project = os.path.join(project_root, 'config', config_path)
    if os.path.exists(config_path_project):
        print(f"Found config file at: {config_path_project}")
        with open(config_path_project, 'r') as f:
            return yaml.safe_load(f)
    
    # Try config/ directory relative to module location
    config_path_module = os.path.join(module_dir, 'config', config_path)
    if os.path.exists(config_path_module):
        print(f"Found config file at: {config_path_module}")
        with open(config_path_module, 'r') as f:
            return yaml.safe_load(f)
    
    # Config file not found
    print(f"Warning: Config file '{config_path}' not found. Using defaults.")
    return None

def list_files(directory):
    """List all GPX files in the specified directory."""
    if not os.path.exists(directory):
        print(f"Warning: Directory '{directory}' does not exist.")
        return []
    
    file_list = []
    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.lower().endswith(".gpx"):
                file_list.append(os.path.join(root, file_name))
    if file_list:
        print("Files in the input directory:")
        for file_path in file_list:
            print(file_path)
    else:
        print(f"No files found in the input directory {directory}.")
    return file_list

def backup_file(file_path, backup_path):
    """Move the specified file to the backup directory."""
    if os.path.isfile(backup_path):
        if filecmp.cmp(file_path, backup_path, shallow=True):
            print(f"Backup file of {file_path} already exists "
                  "and appears to be equal: Copy skipped.")
        else:
            shutil.move(backup_path, backup_path + ".bak")
            shutil.copy(file_path, backup_path)
            print(f"File {file_path} already exists in backup directory: "
                  ".bak appended to old file.")
    else:
        shutil.copy(file_path, backup_path)
        print(f"Backup of input file {file_path} created.")

def check_file(file_path):
    """Check if the specified file exists and create a backup copy if it does."""
    if os.path.isfile(file_path):
        shutil.move(file_path, file_path + ".bak")
        print(f"File {file_path} already existed: .bak appended to old file.")

def read_file(file_path):
    """Read the specified file and return its contents as a list of strings."""
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines

def write_file(file_path, lines):
    """Write the specified list of strings to a file."""
    with open(file_path, 'w') as file:
        file.writelines(lines)
