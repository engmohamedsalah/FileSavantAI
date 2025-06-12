#!/usr/bin/env python3
"""
FileSavantAI with Simplified MCP-like Communication
Fast C-Python communication using JSON-RPC over pipes
"""

import os
import json
import argparse
import subprocess
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import OpenAI
try:
    import openai
except ImportError:
    print("❌ OpenAI library not found. Please install: pip install openai")
    exit(1)

def run_file_info_simple_rpc(directory=".", suppress_errors=False):
    """Use simple JSON-RPC to get file information quickly"""
    try:
        # Start the server process
        process = subprocess.Popen(
            ['./file_info_mcp_server'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send list_files request directly (skip complex initialization)
        request = f'{{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{{"name":"list_files","arguments":{{"directory":"{directory}"}}}}}}\n'
        
        # Write request and close stdin to signal completion
        process.stdin.write(request)
        process.stdin.close()
        
        # Read all output
        output = ""
        for line in process.stdout:
            output += line
            # Look for the result we need
            if '"result":[' in line:
                try:
                    # Find the JSON response with the file list
                    start = line.find('{"jsonrpc"')
                    if start != -1:
                        json_response = line[start:].strip()
                        response_data = json.loads(json_response)
                        if "result" in response_data:
                            return response_data["result"]
                except json.JSONDecodeError:
                    continue
        
        process.wait()
        return []
        
    except Exception as e:
        if not suppress_errors:
            print(f"❌ Error communicating with file server: {e}")
        return []

# Import all the other functions from the original file
def find_file(files, filename, match_type="contains", case_sensitive=False):
    """Find files matching the criteria"""
    matching_files = []
    search_name = filename if case_sensitive else filename.lower()
    
    for file_info in files:
        file_name = file_info["name"]
        compare_name = file_name if case_sensitive else file_name.lower()
        
        if match_type == "exact":
            if compare_name == search_name:
                matching_files.append(file_info)
        elif match_type == "contains":
            if search_name in compare_name:
                matching_files.append(file_info)
        elif match_type == "similar":
            if search_name in compare_name or compare_name in search_name:
                matching_files.append(file_info)
    
    return matching_files

def format_timestamp(timestamp):
    """Format Unix timestamp to readable date"""
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))

def format_file_size(size):
    """Format file size in human readable format"""
    if size < 1024:
        return f"{size}.0 B"
    elif size < 1024 * 1024:
        return f"{size/1024:.1f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size/(1024*1024):.1f} MB"
    elif size < 1024 * 1024 * 1024 * 1024:
        return f"{size/(1024*1024*1024):.1f} GB"
    elif size < 1024 * 1024 * 1024 * 1024 * 1024:
        return f"{size/(1024*1024*1024*1024):.1f} TB"
    else:
        return f"{size/(1024*1024*1024*1024*1024):.1f} PB"

def extract_query_parameters(query, suppress_warnings=False):
    """Use AI to extract structured parameters from natural language query"""
    # Set up OpenAI API key
    openai.api_key = os.getenv('OPENAI_API_KEY')
    if not openai.api_key:
        return {
            "match_type": "contains",
            "case_sensitive": False,
            "intent": "basic file analysis"
        }
    
    system_prompt = """You are a parameter extraction assistant. Extract file search parameters from natural language queries.

Return ONLY a JSON object with these exact keys:
- "match_type": "exact", "contains", or "similar"
- "case_sensitive": true or false
- "intent": brief description of the user's intent

Examples:
"find exact match for myfile.txt" → {"match_type": "exact", "case_sensitive": false, "intent": "exact file search"}
"case-sensitive search for Config.py" → {"match_type": "contains", "case_sensitive": true, "intent": "case-sensitive file search"}

For unclear queries, default to: {"match_type": "contains", "case_sensitive": false, "intent": "general file search"}"""

    try:
        model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extract parameters from: {query}"}
            ],
            max_tokens=100,
            temperature=0.1
        )
        
        result = response.choices[0].message.content.strip()
        params = json.loads(result)
        
        if all(key in params for key in ["match_type", "case_sensitive"]):
            return params
        else:
            return {
                "match_type": "contains",
                "case_sensitive": False,
                "intent": "fallback file analysis"
            }
            
    except Exception as e:
        if not suppress_warnings:
            print(f"⚠️ AI parameter extraction failed: {e}")
        return {
            "match_type": "contains",
            "case_sensitive": False,
            "intent": "error fallback"
        }

def answer_file_question_with_ai(files, query, filename=None, suppress_warnings=False):
    """Use OpenAI to intelligently answer questions about file attributes"""
    if not files:
        return "❌ No files found to analyze."
    
    # If filename specified, extract parameters and filter files
    if filename:
        params = extract_query_parameters(query, suppress_warnings)
        match_type = params["match_type"]
        case_sensitive = params["case_sensitive"]
        
        if not (target_files := find_file(files, filename, match_type, case_sensitive)):
            return f"❌ File '{filename}' not found."
        files = target_files
    
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
    
    system_prompt = """You are a file system expert assistant. Analyze file metadata and answer natural language queries about files.
    
    Provide clear, accurate answers based on the file data. Use emojis for better readability.
    For ownership questions, provide both username and UID.
    For permission questions, explain what the permissions mean."""
    
    user_prompt = f"""Query: {query}

File Data:
{json.dumps(file_data_summary, indent=2)}

Please analyze this file information and answer the query clearly and accurately."""
    
    try:
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
        if not suppress_warnings:
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
            responses.append(f"📁 {file_info['name']} - Owner: {file_info['owner']}, Size: {format_file_size(file_info['size'])}, Permissions: {file_info['permissions_readable']}")
    return "\n\n".join(responses)

def main():
    parser = argparse.ArgumentParser(description="FileSavantAI with Fast MCP Communication")
    parser.add_argument("--dir", default=".", help="Directory to search (default: current)")
    parser.add_argument("--filename", help="Specific file to analyze")
    parser.add_argument("--query", default="show me detailed information about all files", help="Natural language query about the file(s)")
    parser.add_argument("--validate", action="store_true", help="Validate results with ls -l")

    args = parser.parse_args()

    print(f"🔍 Analyzing files in '{args.dir}' using fast MCP communication...")
    
    # Use simplified RPC to get file information quickly
    files = run_file_info_simple_rpc(args.dir)
    if not files:
        print("❌ No files found or error getting file information")
        return
        
    print(f"✅ Found {len(files)} files")
    
    # Check OpenAI API availability first
    api_key = os.getenv('OPENAI_API_KEY')
    has_openai = api_key is not None and api_key.strip() != ""
    
    if has_openai:
        print(f"\n🤖 AI Analysis for '{args.filename if args.filename else 'all files'}':")
        openai.api_key = api_key
        answer = answer_file_question_with_ai(files, args.query, args.filename)
    else:
        print(f"\n📝 Basic Analysis for '{args.filename if args.filename else 'all files'}' (No OpenAI API key):")
        # Filter files if filename specified
        if args.filename:
            target_files = find_file(files, args.filename, "contains", False)
            if not target_files:
                print(f"❌ File '{args.filename}' not found.")
                return
            files = target_files
        answer = fallback_file_analysis(files, args.query)
    
    print(answer)

if __name__ == "__main__":
    main() 