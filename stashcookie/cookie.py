import argparse
import os
import subprocess
from pathlib import Path


def upload_file(file_path: str, projectname: str):
    """Uploads a single file to AWS S3 Glacier Deep Archive."""
    file = Path(file_path.strip())

    if not file.exists():
        print(f"⚠️ Skipping: {file} (File not found)")
        return

    cmd = f'aws s3 cp "{file}" s3://{projectname} --storage-class DEEP_ARCHIVE'
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
        
        # Write to .cookie.env
        env_file = Path(".cookie.env")
        env_file.write_text(f"projectname={project_name}\n")

        print(f"✅ Project name saved: {project_name}")
        print("📂 .cookie.env file created!")

        cmd = f'''aws s3 mb s3://{project_name}'''
        os.system(cmd)
        print(f"🪣 aws s3 bucket created {project_name}")

    if args.command == "upload-all":
        with open(".cookie.env", "r") as inf:
            projectname = [o.strip("\n").split('=')[1] for o in inf if "projectname=" in o][0]

        os.system("rm .cookie.s3inventory") # reset the inventory

        with open(".cookie_files.txt", "r") as file_list:
            for file_path in file_list:
                if file_path.strip():
                    upload_file(file_path, projectname)

    if args.command == "check":
        with open(".cookie.env", "r") as inf:
            projectname = [o.strip("\n").split('=')[1] for o in inf if "projectname=" in o][0]

        cmd=f'''aws s3 ls s3://{projectname} > .cookie.s3inventory'''
        
        print(cmd)
        os.system(cmd)

        # Define input and output files
        input_file = ".cookie_files.txt"
        output_file = ".tmp"

        # Ensure .cookie_files.txt exists
        if not Path(input_file).exists():
            print(f"❌ Error: {input_file} not found!")
            exit(1)

        local = {}
        with open(input_file, "r", encoding="utf-8") as f, open(output_file, "w", encoding="utf-8") as out:
            for line in f:
                file_path = line.strip()  # Remove spaces & newlines

                # Print for debugging
                print(f"Processing: {file_path}")

                path = Path(file_path)
                if path.exists() and path.is_file():
                    file_size = path.stat().st_size
                    local[Path(file_path).name] = file_size
                    print(f"✅ Saved: {file_path} ({file_size} bytes)")
                else:
                    out.write(f"Warning: File not found: {file_path}\n")
                    print(f"⚠️ Skipping: {file_path} (File not found)")


        # Define input and output files
        input_file = ".cookie.s3inventory"
        output_file = ".tmp_s3"

        # Ensure .cookie.s3inventory exists
        if not Path(input_file).exists():
            print(f"❌ Error: {input_file} not found!")
            exit(1)

        ons3 = {}
        with open(input_file, "r", encoding="utf-8") as f, open(output_file, "w", encoding="utf-8") as out:
            for line in f:
                parts = line.strip().split()
                
                # Expecting format: "DATE TIME SIZE FILENAME"
                if len(parts) < 3:
                    print(f"⚠️ Skipping invalid line: {line.strip()}")
                    continue
                
                file_size = parts[-2]  # Second last part is the size
                file_name = parts[-1]  # Last part is the filename

                ons3[file_name] = file_size

                # Write to output file
                out.write(f"{file_name} {file_size}\n")


        with open(".cookie.todo", "w") as of:
            for key in local:
                if key not in ons3 or ons3[key] != ons3[key]:
                    of.write(key + "\n")

        os.system("rm .tmp .tmp_s3")

if __name__ == "__main__":
    main()
