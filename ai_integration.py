import subprocess
import argparse
import json
import os
from datetime import datetime

def run_file_info(directory="."):
    """Run the enhanced file_info C program and capture its JSON output"""
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
    """Parse the JSON output from the enhanced C program"""
    try:
        files = json.loads(output)
        return files if isinstance(files, list) else [files]
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print(f"Raw output: {output}")
        return []

def find_file(files, filename, match_type="contains", case_sensitive=False):
    """Find files matching the given criteria"""
    matches = []
    search_term = filename if case_sensitive else filename.lower()
    
    for file in files:
        file_name = file["name"] if case_sensitive else file["name"].lower()
        
        if match_type == "exact":
            if file_name == search_term:
                matches.append(file)
        elif match_type == "contains":
            if search_term in file_name:
                matches.append(file)
        elif match_type == "similar":
            # Simple similarity check
            if search_term in file_name or any(word in file_name for word in search_term.split()):
                matches.append(file)
    
    return matches

def format_timestamp(timestamp):
    """Convert Unix timestamp to readable format"""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def format_file_size(size):
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"

def analyze_file_ownership(file_info):
    """Analyze and describe file ownership details"""
    analysis = [
        f"📁 File: {file_info['name']}",
        f"👤 Owner: {file_info['owner']} (UID: {file_info['uid']})",
        f"👥 Group: {file_info['group']} (GID: {file_info['gid']})",
        f"📏 Size: {format_file_size(file_info['size'])}",
        f"📅 Modified: {format_timestamp(file_info['modified'])}",
        f"🔐 Permissions: {file_info['permissions_readable']} ({file_info['permissions']})",
        f"📂 Type: {file_info['type']}"
    ]
    
    return "\n".join(analysis)

def answer_ownership_question(files, question, filename=None):
    """Answer questions about file ownership and attributes"""
    if not files:
        return "❌ No files found to analyze."
    
    # If filename specified, filter to that file
    if filename:
        if not (target_files := find_file(files, filename, "contains")):
            return f"❌ File '{filename}' not found."
        files = target_files
    
    responses = []
    
    for file_info in files:
        if "who owns" in question.lower() or "owner" in question.lower():
            responses.append(f"🔍 {file_info['name']} is owned by {file_info['owner']} (UID: {file_info['uid']})")
        
        elif "who created" in question.lower() or "creator" in question.lower():
            responses.append(f"🔍 {file_info['name']} was created by {file_info['owner']} (files show owner, not creator)")
        
        elif "permission" in question.lower() or "access" in question.lower():
            responses.append(f"🔍 {file_info['name']} permissions: {file_info['permissions_readable']} ({file_info['permissions']})")
        
        elif "size" in question.lower():
            responses.append(f"🔍 {file_info['name']} size: {format_file_size(file_info['size'])}")
        
        elif "when" in question.lower() or "modified" in question.lower():
            responses.append(f"🔍 {file_info['name']} last modified: {format_timestamp(file_info['modified'])}")
        
        elif "group" in question.lower():
            responses.append(f"🔍 {file_info['name']} group: {file_info['group']} (GID: {file_info['gid']})")
        
        else:
            # Provide comprehensive info for general questions
            responses.append(analyze_file_ownership(file_info))
    
    return "\n\n".join(responses)

def validate_with_ls(file_path):
    """Validate results with ls -l command"""
    try:
        ls_output = subprocess.check_output(['ls', '-l', file_path], text=True)
        return ls_output.strip()
    except Exception as e:
        return f"Error running ls -l: {e}"

def main():
    parser = argparse.ArgumentParser(description="Enhanced AI File Analyzer - Ask questions about file ownership and attributes")
    parser.add_argument("--dir", default=".", help="Directory to search (default: current)")
    parser.add_argument("--filename", help="Specific file to analyze")
    parser.add_argument("--question", default="who owns", help="Question to ask about the file(s)")
    parser.add_argument("--match-type", choices=["exact", "contains", "similar"], default="contains", help="How to match filenames")
    parser.add_argument("--case-sensitive", action="store_true", help="Case sensitive filename matching")
    parser.add_argument("--validate", action="store_true", help="Validate results with ls -l")
    parser.add_argument("--list-all", action="store_true", help="List all files with detailed info")
    
    args = parser.parse_args()

    print(f"🔍 Analyzing files in '{args.dir}'...")
    
    # Run the enhanced C program
    output = run_file_info(args.dir)
    if not output:
        return
    
    # Parse JSON files
    files = parse_file_info(output)
    if not files:
        print("❌ No files found or error parsing output")
        return
        
    print(f"✅ Found {len(files)} files")
    
    if args.list_all:
        print(f"\n📋 All files in '{args.dir}':")
        for file_info in files:
            print(f"\n{analyze_file_ownership(file_info)}")
    else:
        # Answer the specific question
        if args.filename:
            print(f"\n🤖 AI Analysis for '{args.filename}':")
        else:
            print(f"\n🤖 AI Analysis for all files:")
        
        answer = answer_ownership_question(files, args.question, args.filename)
        print(answer)
    
    # Validation with ls -l
    if args.validate:
        print(f"\n🔎 Validation with 'ls -l':")
        if args.filename:
            target_files = find_file(files, args.filename, args.match_type, args.case_sensitive)
        else:
            target_files = files[:3]  # Limit to first 3 files for validation
            
        for file_info in target_files:
            file_path = os.path.join(args.dir, file_info['name']) if args.dir != "." else file_info['name']
            ls_result = validate_with_ls(file_path)
            print(f"  {file_info['name']}:")
            print(f"    {ls_result}")

if __name__ == "__main__":
    main()