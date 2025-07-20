import argparse
import os
import subprocess
from pathlib import Path

def upload_file(file_path: str, projectname: str, storage_class: str = "DEEP_ARCHIVE"):
    """Uploads a single file to AWS S3 Glacier Deep Archive."""
    file = Path(file_path.strip())
    if not file.exists():
        print(f"⚠️ Skipping: {file} (File not found)")
        return
    cmd = f'aws s3 cp "{file}" s3://{projectname} --storage-class {storage_class}'
    print(f"🚀 Uploading: {file}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Successfully uploaded: {file}")
    else:
        print(f"❌ Upload failed: {file}\n{result.stderr}")

def main():
    parser = argparse.ArgumentParser(description="Cookie CLI: Manage Amazon Glacier backups.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Init command
    subparsers.add_parser("init", help="Initialize project settings")
    
    # Upload all files
    subparsers.add_parser("upload-all", help="Upload all files from .cookie_files.txt")
    
    # Upload a single file
    upload_parser = subparsers.add_parser("upload", help="Upload a single file")
    upload_parser.add_argument("file", type=str, help="Path to the file to upload")
    
    # Check command
    subparsers.add_parser("check", help="Check the S3 inventory")
    
    args = parser.parse_args()
    
    if args.command == "upload":
        with open(".cookie.env", "r") as inf:
            projectname = [o.strip("\n").split('=')[1] for o in inf if "projectname=" in o][0]
        upload_file(args.file, projectname=projectname)
    
    if args.command == "init":
        print("✅ Initializing stashcookie...")
        
        # Request project name from user
        project_name = input("Enter project name: ").strip()
        
        if not project_name:
            print("❌ Error: Project name cannot be empty.")
            return
            
        storage_class = input("Enter S3 storage class (default: DEEP_ARCHIVE): ").strip()
        if not storage_class:
            storage_class = "DEEP_ARCHIVE"
        
        # Write to .cookie.env - FIXED: Define env_file before using it
        env_file = Path(".cookie.env")
        with env_file.open("w", encoding="utf-8") as f:  # Changed to "w" to write both values together
            f.write(f"projectname={project_name}\n")
            f.write(f"storage_class={storage_class}\n")
            
        print(f"✅ Project name saved: {project_name}")
        print("📂 .cookie.env file created!")
        
        bucket_check_cmd = f'aws s3 ls s3://{project_name} 2>/dev/null'
        bucket_exists = os.system(bucket_check_cmd) == 0

        if not bucket_exists:
            cmd = f'''aws s3 mb s3://{project_name}'''
            os.system(cmd)
            print(f"🪣 aws s3 bucket created {project_name}")
        else:
            print(f"✅ AWS S3 bucket already exists: {project_name}")

        Path(".cookie_files.txt").touch()
    
    if args.command == "upload-all":
        with open(".cookie.env", "r") as inf:
            projectname = [o.strip("\n").split('=')[1] for o in inf if "projectname=" in o][0]
        os.system("rm -rf .cookie.s3inventory") # reset the inventory
        with open(".cookie_files.txt", "r") as file_list:
            for file_path in file_list:
                if file_path.strip():
                    upload_file(file_path, projectname)
    
    if args.command == "check":
        # Get project name
        with open(".cookie.env", "r") as inf:
            projectname = [o.strip("\n").split('=')[1] for o in inf if "projectname=" in o][0]
        
        # Get S3 file list
        cmd = f'''aws s3 ls s3://{projectname} > .cookie.s3inventory'''
        print(cmd)
        os.system(cmd)
        
        # Get local files
        local_files = set()
        with open(".cookie_files.txt", "r") as f:
            for line in f:
                file_path = line.strip()
                if Path(file_path).exists():
                    local_files.add(Path(file_path).name)
        
        # Get S3 files
        s3_files = set()
        with open(".cookie.s3inventory", "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 4:  # DATE TIME SIZE FILENAME
                    s3_files.add(parts[-1])  # filename
        
        # Find local files not on S3
        missing_from_s3 = local_files - s3_files
        
        # Write todo list
        with open(".cookie.todo", "w") as f:
            for filename in missing_from_s3:
                f.write(filename + "\n")

if __name__ == "__main__":
    main()