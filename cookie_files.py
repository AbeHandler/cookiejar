from pathlib import Path

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


from pathlib import Path

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
    print(ons3[key] == ons3[key])

