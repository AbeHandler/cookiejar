import argparse
import os
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Cookie CLI: Manage Amazon Glacier backups.")
    parser.add_argument("command", choices=["init", "upload", "check"], help="Available commands: init")

    args = parser.parse_args()

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

    if args.command == "upload":
        with open(".cookie.env", "r") as inf:
            projectname = [o.strip("\n").split('=')[1] for o in inf if "projectname=" in o][0]

        os.system("rm .cookie.s3inventory") # reset the inventory

        for _ in open(".cookie_files.txt"):
            if len(_) > 1:
                cmd = f'''aws s3 cp {_} s3://{projectname} --storage-class DEEP_ARCHIVE'''
                print(f"uploading ... {_}")
                os.system(cmd)

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

        for key in local:
            assert ons3[key] == ons3[key]

        os.system("rm .tmp .tmp_s3")

if __name__ == "__main__":
    main()
