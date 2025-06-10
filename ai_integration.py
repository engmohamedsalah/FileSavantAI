import subprocess
import json
import os
import openai
import argparse
import difflib
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Configure OpenAI API key
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Please set it in your environment or in a .env file.")
openai.api_key = api_key

def run_file_info():
    """Run the file_info C program and capture its output"""
    try:
        # Execute the compiled C program
        result = subprocess.run(['./file_info'], 
                               capture_output=True, 
                               text=True, 
                               check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running file_info: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def parse_file_info(output):
    """Parse the output from file_info into a structured format"""
    files = []
    for line in output.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.split()
        # Expected format: permissions links owner group size month day time name
        if len(parts) >= 8:
            file_data = {
                "permissions": parts[0],
                "links": parts[1],
                "owner": parts[2],
                "group": parts[3],
                "size": parts[4],
                "date": f"{parts[5]} {parts[6]}",
                "time": parts[7],
                "name": " ".join(parts[8:])
            }
            files.append(file_data)
    return files

def analyze_with_ai(files_data):
    """Use OpenAI to analyze file information and provide a concise summary."""
    if not files_data:
        return "No files to analyze."
    
    # Prepare a more concise prompt for OpenAI
    prompt = f"""Briefly summarize the following file system data. Focus on key insights only.
    
    Data:
    {json.dumps(files_data, indent=2)}

    Provide a short, bulleted summary covering:
    - A one-sentence overview of the directory.
    - Any standout files (e.g., largest, executable).
    - A key security or organization recommendation.
    """

    try:
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are FileSavantAI, an intelligent file system analyzer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error analyzing files with AI: {e}"

def get_specific_file_info(files_data, filename_to_find, match_type='exact', case_sensitive=False):
    """Find and print details for files based on matching criteria."""
    
    found_files = []
    
    # Prepare search term based on case sensitivity
    search_term = filename_to_find if case_sensitive else filename_to_find.lower()

    if match_type == 'exact':
        for file in files_data:
            prepared_file_name = file["name"].strip() if case_sensitive else file["name"].strip().lower()
            if prepared_file_name == search_term:
                found_files.append(file)

    elif match_type == 'contains':
        for file in files_data:
            prepared_file_name = file["name"].strip() if case_sensitive else file["name"].strip().lower()
            if search_term in prepared_file_name:
                found_files.append(file)

    elif match_type == 'similar':
        all_filenames = [f["name"].strip() for f in files_data]
        # Handle case for similarity search
        if case_sensitive:
            similar_matches = difflib.get_close_matches(search_term, all_filenames, n=3, cutoff=0.6)
        else:
            # Create a mapping from lowercase to original case
            lower_to_original = {name.lower(): name for name in all_filenames}
            similar_matches_lower = difflib.get_close_matches(search_term, lower_to_original.keys(), n=3, cutoff=0.6)
            similar_matches = [lower_to_original[m] for m in similar_matches_lower]

        if similar_matches:
            print(f"\n🤔 No exact match found. Did you mean one of these?")
            for match_name in similar_matches:
                for file in files_data:
                    if file["name"].strip() == match_name:
                        found_files.append(file)

    if not found_files:
        print(f"\nℹ️ No files found matching '{filename_to_find}' with the specified criteria.")
        return

    print(f"\n📄 Found {len(found_files)} matching file(s):")
    for file in found_files:
        print("-" * 20)
        print(f"File: {file['name']}")
        print(f"Owner: {file['owner']}")
        print(f"Group: {file['group']}")
        print(f"Permissions: {file['permissions']}")
        print(f"Size: {file['size']} bytes")
        print(f"Last Modified: {file['date']} {file['time']}")

def main():
    parser = argparse.ArgumentParser(description="FileSavantAI - Analyze file system and get details for a specific file.")
    parser.add_argument("filename", help="The name of the file to search for.")
    parser.add_argument("--case-sensitive", action="store_true", help="Perform a case-sensitive search.")
    parser.add_argument("--match-type", choices=['exact', 'contains', 'similar'], default='exact', help="The type of matching to perform.")
    args = parser.parse_args()

    print("🔍 FileSavantAI - Intelligent File System Analysis")
    print("=================================================")
    
    # Run the C program and get output
    print("\nRunning file analysis...")
    output = run_file_info()
    
    if not output:
        print("❌ Failed to get file information.")
        return
    
    # Parse the output
    files_data = parse_file_info(output)
    print(f"✅ Found {len(files_data)} files.")
    
    # Analyze with AI
    print("\nAnalyzing with AI...")
    analysis = analyze_with_ai(files_data)
    
    # Display results
    print("\n📊 AI Analysis Results:")
    print("=======================")
    print(analysis)
    
    # Get info for the specified file
    get_specific_file_info(files_data, args.filename, args.match_type, args.case_sensitive)
    
    # Validate with ls -l (only makes sense for an exact match)
    if args.match_type == 'exact':
        print(f"\n🔎 Validating with 'ls -l {args.filename}':")
        try:
            ls_output = subprocess.check_output(['ls', '-l', args.filename], text=True)
            print(ls_output)
        except Exception as e:
            print(f"Could not validate '{args.filename}': {e}")

if __name__ == "__main__":
    main()