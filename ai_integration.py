import subprocess
import argparse
import os

def run_file_info(directory="."):
    """Run the file_info C program and capture its output"""
    try:
        result = subprocess.run(['./file_info', directory], 
                               capture_output=True, 
                               text=True, 
                               check=True)
        return result.stdout
    except Exception as e:
        print(f"Error running file_info: {e}")
        return None

def parse_file_info(output):
    """Parse the simplified output: 'size bytes filename'"""
    files = []
    for line in output.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) >= 3 and parts[1] == "bytes":
            files.append({
                "size": parts[0],
                "name": " ".join(parts[2:])
            })
    return files

def find_file(files, filename):
    """Find files matching the given name"""
    return [file for file in files if filename.lower() in file["name"].lower()]

def main():
    parser = argparse.ArgumentParser(description="Simple File Analyzer")
    parser.add_argument("filename", help="File to search for")
    parser.add_argument("--dir", default=".", help="Directory to search (default: current)")
    args = parser.parse_args()

    print(f"🔍 Analyzing files in '{args.dir}'...")
    
    # Run the C program
    output = run_file_info(args.dir)
    if not output:
        return
    
    # Parse files
    files = parse_file_info(output)
    print(f"Found {len(files)} files")
    
    # Find matching files
    matches = find_file(files, args.filename)
    
    if matches:
        print(f"\n📄 Found {len(matches)} matching file(s):")
        for file in matches:
            print(f"  {file['name']} - {file['size']} bytes")
        
        # Validation with ls -l for exact matches
        print(f"\n🔎 Validating with 'ls -l':")
        for file in matches:
            try:
                file_path = os.path.join(args.dir, file['name']) if args.dir != "." else file['name']
                ls_output = subprocess.check_output(['ls', '-l', file_path], text=True)
                print(f"  {file['name']}:")
                print(f"    {ls_output.strip()}")
            except Exception as e:
                print(f"  Could not validate '{file['name']}': {e}")
    else:
        print(f"\n❌ No files found matching '{args.filename}'")

if __name__ == "__main__":
    main()