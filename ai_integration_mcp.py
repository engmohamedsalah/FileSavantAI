#!/usr/bin/env python3
"""
FileSavantAI with MCP Integration
AI-powered file analysis using Model Context Protocol for C-Python communication
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

class MCPFileClient:
    """MCP Client for communicating with file_info_mcp_server"""
    
    def __init__(self):
        self.server_process = None
        self.request_id = 1
    
    def start_server(self):
        """Start the MCP server process"""
        try:
            self.server_process = subprocess.Popen(
                ['./file_info_mcp_server'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0
            )
            # Read the initialization message
            init_line = self.server_process.stdout.readline()
            if init_line:
                # Send initialize request
                init_request = {
                    "jsonrpc": "2.0",
                    "id": self.request_id,
                    "method": "initialize",
                    "params": {}
                }
                request_json = json.dumps(init_request) + "\n"
                self.server_process.stdin.write(request_json)
                self.server_process.stdin.flush()
                self.request_id += 1
                
                # Read initialize response
                response_line = self.server_process.stdout.readline()
                if response_line:
                    return True
            return False
        except Exception as e:
            print(f"❌ Failed to start MCP server: {e}")
            return False
    
    def send_request(self, method, params=None):
        """Send MCP request and get response"""
        if not self.server_process:
            return None
            
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method
        }
        
        if params:
            request["params"] = params
            
        request_json = json.dumps(request) + "\n"
        
        try:
            self.server_process.stdin.write(request_json)
            self.server_process.stdin.flush()
            
            response_line = self.server_process.stdout.readline()
            if response_line:
                response = json.loads(response_line)
                self.request_id += 1
                return response
        except Exception as e:
            print(f"❌ MCP communication error: {e}")
            
        return None
    
    def list_files(self, directory="."):
        """List files in directory using MCP"""
        response = self.send_request("tools/call", {
            "name": "list_files",
            "arguments": {"directory": directory}
        })
        
        if response and "result" in response:
            return response["result"]
        elif response and "error" in response:
            print(f"❌ MCP Error: {response['error']['message']}")
        
        return []
    
    def stop_server(self):
        """Stop the MCP server process"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()

def run_file_info_mcp(directory="."):
    """Use MCP to get file information"""
    client = MCPFileClient()
    
    if not client.start_server():
        return []
    
    try:
        files = client.list_files(directory)
        return files
    finally:
        client.stop_server()

def parse_file_info(files_data):
    """Parse file information (now directly from MCP response)"""
    if isinstance(files_data, list):
        return files_data
    return []

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
            # Simple similarity check (could be enhanced)
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
    return extract_query_parameters_with_ai(query, suppress_warnings)

def extract_query_parameters_with_ai(query, suppress_warnings=False):
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

Return ONLY a JSON object with these exact keys:
- "match_type": "exact", "contains", or "similar"
- "case_sensitive": true or false
- "intent": brief description of the user's intent

Examples:
"find exact match for myfile.txt" → {"match_type": "exact", "case_sensitive": false, "intent": "exact file search"}
"case-sensitive search for Config.py" → {"match_type": "contains", "case_sensitive": true, "intent": "case-sensitive file search"}
"show similar files to document" → {"match_type": "similar", "case_sensitive": false, "intent": "similar file search"}

For unclear queries, default to: {"match_type": "contains", "case_sensitive": false, "intent": "general file search"}"""

    try:
        # Get model from environment or default to gpt-3.5-turbo
        model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extract parameters from: {query}"}
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
        # Use AI to extract parameters from natural language
        params = extract_query_parameters(query, suppress_warnings)
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
    parser = argparse.ArgumentParser(description="Enhanced AI File Analyzer with MCP - Natural language queries about files")
    parser.add_argument("--dir", default=".", help="Directory to search (default: current)")
    parser.add_argument("--filename", help="Specific file to analyze")
    parser.add_argument("--query", default="show me detailed information about all files", help="Natural language query about the file(s)")
    parser.add_argument("--validate", action="store_true", help="Validate results with ls -l")

    args = parser.parse_args()

    print(f"🔍 Analyzing files in '{args.dir}' using MCP...")
    
    # Use MCP to get file information
    files = run_file_info_mcp(args.dir)
    if not files:
        print("❌ No files found or error getting file information")
        return
        
    print(f"✅ Found {len(files)} files via MCP")
    
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