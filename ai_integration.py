import subprocess
import argparse
import json
import os
from datetime import datetime
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

def extract_query_parameters(query):
    """Use AI to extract structured parameters from natural language query"""
    return extract_query_parameters_with_ai(query)

def extract_query_parameters_with_ai(query):
    """Use AI to extract structured parameters from natural language query"""
    
    # Set up OpenAI API key
    openai.api_key = os.getenv('OPENAI_API_KEY')
    if not openai.api_key:
        # Simple fallback if no AI available
        return {
            "match_type": "contains",
            "case_sensitive": False,
            "intent": "basic file analysis"
        }
    
    system_prompt = """You are a parameter extraction assistant. Extract file search parameters from natural language queries.

    Return ONLY valid JSON with these exact keys:
    {
        "match_type": "exact" | "contains" | "similar",
        "case_sensitive": true | false,
        "intent": "brief description of what user wants"
    }

    Rules:
    - "exact match", "exact file", "precise" → "exact"
    - "similar", "fuzzy", "approximate" → "similar"  
    - Default → "contains"
    - "case-sensitive", "case sensitive" → true
    - Default case_sensitive → false"""
    
    user_prompt = f"""Extract parameters from this query: "{query}"

    Return only JSON, no other text."""
    
    try:
        model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=100,
            temperature=0.1  # Low temperature for consistent parsing
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse the JSON response
        import json
        params = json.loads(result)
        
        # Validate required keys
        if all(key in params for key in ["match_type", "case_sensitive"]):
            return params
        else:
            # Fallback if AI response is malformed
            return {
                "match_type": "contains",
                "case_sensitive": False,
                "intent": "fallback file analysis"
            }
            
    except Exception as e:
        print(f"⚠️ AI parameter extraction failed: {e}")
        return {
            "match_type": "contains",
            "case_sensitive": False,
            "intent": "error fallback"
        }



def answer_file_question_with_ai(files, query, filename=None):
    """Use OpenAI to intelligently answer questions about file attributes"""
    if not files:
        return "❌ No files found to analyze."
    
    # If filename specified, extract parameters and filter files
    if filename:
        # Use AI to extract parameters from natural language
        params = extract_query_parameters(query)
        match_type = params["match_type"]
        case_sensitive = params["case_sensitive"]
        
        if not (target_files := find_file(files, filename, match_type, case_sensitive)):
            return f"❌ File '{filename}' not found."
        files = target_files
    
    # Set up OpenAI API key
    openai.api_key = os.getenv('OPENAI_API_KEY')
    if not openai.api_key:
        return "❌ OpenAI API key not found. Please set OPENAI_API_KEY in .env file"
    
    # Prepare file data for AI analysis
    file_data_summary = []
    for file_info in files:
        file_summary = {
            "name": file_info["name"],
            "size": format_file_size(file_info["size"]),
            "owner": f"{file_info['owner']} (UID: {file_info['uid']})",
            "group": f"{file_info['group']} (GID: {file_info['gid']})",
            "permissions": f"{file_info['permissions_readable']} ({file_info['permissions']})",
            "type": file_info["type"],
            "modified": format_timestamp(file_info["modified"]),
            "accessed": format_timestamp(file_info["accessed"]),
            "changed": format_timestamp(file_info["changed"])
        }
        file_data_summary.append(file_summary)
    
    # Create AI prompt
    system_prompt = """You are a file system expert assistant. You analyze file metadata and answer natural language queries about files.
    
    Available file information includes:
    - File name, size, type
    - Owner (username and UID)
    - Group (group name and GID) 
    - Permissions (readable format and octal)
    - Timestamps (modified, accessed, changed)
    
    You can understand queries that include specifications like:
    - "exact match" vs "contains" vs "similar" matching
    - "case-sensitive" or "case sensitive" requirements
    - Detailed information requests
    - Ownership, permission, size, and timestamp questions
    
    Provide clear, accurate answers based on the file data. Use emojis for better readability.
    For ownership questions, provide both username and UID.
    For permission questions, explain what the permissions mean.
    Be helpful and informative."""
    
    user_prompt = f"""Query: {query}

File Data:
{json.dumps(file_data_summary, indent=2)}

Please analyze this file information and answer the query clearly and accurately."""
    
    try:
        # Get model from environment or default to gpt-3.5-turbo
        model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        ai_answer = response.choices[0].message.content.strip()
        return f"🤖 AI Analysis:\n{ai_answer}"
        
    except Exception as e:
        # Fallback to simple analysis if AI fails
        print(f"⚠️ AI analysis failed: {e}")
        return fallback_file_analysis(files, query)

def fallback_file_analysis(files, query):
    """Fallback analysis when AI is unavailable"""
    responses = []
    for file_info in files:
        if "own" in query.lower():
            responses.append(f"📁 {file_info['name']} is owned by {file_info['owner']} (UID: {file_info['uid']})")
        elif "permission" in query.lower():
            responses.append(f"🔐 {file_info['name']} permissions: {file_info['permissions_readable']} ({file_info['permissions']})")
        elif "size" in query.lower():
            responses.append(f"📏 {file_info['name']} size: {format_file_size(file_info['size'])}")
        else:
            # Provide basic file info as fallback
            responses.append(f"📁 {file_info['name']} - Owner: {file_info['owner']}, Size: {format_file_size(file_info['size'])}, Permissions: {file_info['permissions_readable']}")
    return "\n\n".join(responses)

def validate_with_ls(file_path):
    """Validate results with ls -l command"""
    try:
        ls_output = subprocess.check_output(['ls', '-l', file_path], text=True)
        return ls_output.strip()
    except Exception as e:
        return f"Error running ls -l: {e}"



def main():
    parser = argparse.ArgumentParser(description="Enhanced AI File Analyzer - Natural language queries about files")
    parser.add_argument("--dir", default=".", help="Directory to search (default: current)")
    parser.add_argument("--filename", help="Specific file to analyze")
    parser.add_argument("--query", default="show me detailed information about all files", help="Natural language query about the file(s)")
    parser.add_argument("--validate", action="store_true", help="Validate results with ls -l")

    
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
    
    # Answer the query using AI
    if args.filename:
        print(f"\n🤖 AI Analysis for '{args.filename}':")
    else:
        print(f"\n🤖 AI Analysis for all files:")
    
    answer = answer_file_question_with_ai(files, args.query, args.filename)
    print(answer)
    
    # Validation with ls -l
    if args.validate:
        print(f"\n🔎 Validation with 'ls -l':")
        if args.filename:
            # Use AI to extract parameters from natural language
            params = extract_query_parameters(args.query)
            match_type = params["match_type"]
            case_sensitive = params["case_sensitive"]
                
            target_files = find_file(files, args.filename, match_type, case_sensitive)
        else:
            target_files = files[:3]  # Limit to first 3 files for validation
            
        for file_info in target_files:
            file_path = os.path.join(args.dir, file_info['name']) if args.dir != "." else file_info['name']
            ls_result = validate_with_ls(file_path)
            print(f"  {file_info['name']}:")
            print(f"    {ls_result}")

if __name__ == "__main__":
    main()