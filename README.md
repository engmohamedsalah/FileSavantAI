# FileSavantAI

An enhanced AI-powered file analysis tool that combines a C program for system-level file operations with Python for intelligent analysis and question answering.

## 🚀 Features

- **Enhanced C Program**: Outputs comprehensive file metadata in JSON format
- **AI Question Answering**: Uses configurable OpenAI models (GPT-3.5-turbo, GPT-4, etc.) for intelligent file analysis
- **Advanced Search**: Multiple match types (exact, contains, similar) with case-sensitive options
- **Cross-Validation**: Validates results using `ls -l` command
- **Rich Metadata**: Includes owner, group, permissions, timestamps, inodes, and more
- **Human-Readable Output**: Beautiful formatting with emojis and readable timestamps
- **Fallback Analysis**: Automatic fallback when AI is unavailable
- **Parameter Validation**: Mutual exclusivity checks for command-line arguments

## 📋 Prerequisites

- **C Compiler**: GCC (for compiling the C program)
- **Python 3.6+**: For the AI integration script
- **Unix/Linux/macOS**: For system calls and `ls` command
- **OpenAI API Key**: For AI-powered analysis (optional - fallback available)

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/engmohamedsalah/FileSavantAI.git
cd FileSavantAI
```

### 2. Compile the C Program
```bash
gcc -o file_info file_info.c
```

### 3. **IMPORTANT: Set up OpenAI API Key**
The AI features require an OpenAI API key. Follow these steps:

```bash
# Step 1: Copy the example file
cp .env.example .env

# Step 2: Edit the .env file and add your OpenAI API key
# Open .env in your favorite editor and replace the placeholder:
nano .env
# or
vim .env
# or
code .env
```

**In the `.env` file, add your actual OpenAI API key:**
```bash
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

> 💡 **Get your OpenAI API key from:** https://platform.openai.com/api-keys
> 
> ⚠️ **Important:** Never commit your `.env` file to version control! It's already in `.gitignore`.

### 4. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 5. Test the Setup
```bash
# Test basic functionality
python3 ai_integration.py --filename hello_world.txt --question "who owns this file"
```

## ⚙️ Detailed Setup

If you need more detailed setup instructions or encounter issues:

### Alternative Python Environment Setup
```bash
# Using virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Model Configuration
You can easily switch between different OpenAI models by editing your `.env` file:

```bash
# For better performance (more expensive)
OPENAI_MODEL=gpt-4

# For latest capabilities  
OPENAI_MODEL=gpt-4-turbo

# For optimized performance
OPENAI_MODEL=gpt-4o

# Back to default (cost-effective)
OPENAI_MODEL=gpt-3.5-turbo
```

### Troubleshooting
- **Missing OpenAI API Key**: The system will fall back to keyword-based analysis
- **Invalid Model Name**: Will use gpt-3.5-turbo as fallback
- **Compilation Issues**: Make sure you have GCC installed (`gcc --version`)
- **Permission Denied**: Make sure the compiled executable has execute permissions (`chmod +x file_info`)

## 🏃 How to Run

### Step-by-Step Running Instructions

1. **Ensure everything is compiled and set up:**
   ```bash
   # Verify C program is compiled
   ls -la file_info
   
   # Verify .env file exists with API key
   cat .env
   ```

2. **Basic Usage Examples:**
   ```bash
   # Ask who owns a specific file
   python3 ai_integration.py --filename hello_world.txt --question "who owns this file"
   
   # Get detailed information about all files
   python3 ai_integration.py --question "show me detailed information about all files"
   
   # Analyze files in a different directory
   python3 ai_integration.py --dir /path/to/your/directory --question "list all files with their details"
   ```

3. **With Validation (recommended for testing):**
   ```bash
   # Get AI analysis and validate with ls -l
   python3 ai_integration.py --filename hello_world.txt --question "who owns this file" --validate
   ```

### 🔑 Environment File Setup (Critical Step)

The `.env` file is **required** for AI functionality. Here's exactly what to do:

1. **Copy the template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the file** (choose your preferred editor):
   ```bash
   # Using nano (beginner-friendly)
   nano .env
   
   # Using vim
   vim .env
   
   # Using VS Code
   code .env
   
   # Using any text editor
   open .env
   ```

3. **Replace the placeholders** with your actual values:
   ```bash
   # Before (in .env.example):
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-3.5-turbo
   
   # After (in your .env file):
   OPENAI_API_KEY=sk-proj-abcd1234efgh5678ijkl9012mnop3456qrst7890uvwx
   OPENAI_MODEL=gpt-3.5-turbo
   ```
   
   **Available Models:**
   - `gpt-3.5-turbo` (default, fast and cost-effective)
   - `gpt-4` (more capable but more expensive)
   - `gpt-4-turbo` (latest GPT-4 with better performance)
   - `gpt-4o` (optimized for speed and efficiency)

4. **Save the file** and verify:
   ```bash
   # Check that your API key is set (should show your key)
   cat .env
   ```

> 🔗 **Get your OpenAI API key here:** https://platform.openai.com/api-keys
> 
> 💰 **Note:** OpenAI API usage is pay-per-use. The system uses GPT-3.5-turbo which is very cost-effective.

## 🔍 Usage

### Basic File Analysis
```bash
# Analyze a specific file
python3 ai_integration.py --filename hello_world.txt --query "who owns this file"

# Get comprehensive information about a file
python3 ai_integration.py --filename hello_world.txt --query "show me all details about this file"

# Validate results with ls -l
python3 ai_integration.py --filename hello_world.txt --query "who owns this file" --validate
```

### Advanced Search Options with Natural Language
```bash
# Exact filename match
python3 ai_integration.py --filename hello_world.txt --query "show exact match with all details"

# Case-sensitive search  
python3 ai_integration.py --filename Hello_World.txt --query "find case-sensitive exact match"

# Search in specific directory
python3 ai_integration.py --dir /path/to/directory --filename config.txt --query "who owns this file"

# Similar matching (fuzzy search)
python3 ai_integration.py --filename hello --query "find similar matches and show ownership"
```

### 🤖 AI-Powered Analysis
The system uses **configurable OpenAI models** (default: GPT-3.5-turbo) to intelligently analyze file metadata and answer natural language questions. When AI is unavailable, it automatically falls back to keyword-based analysis:

```bash
# Ownership questions
python3 ai_integration.py --filename hello_world.txt --query "who owns this file"
python3 ai_integration.py --filename hello_world.txt --query "who created this file"

# Permission questions
python3 ai_integration.py --filename hello_world.txt --query "what are the permissions"
python3 ai_integration.py --filename hello_world.txt --query "can others read this file"

# Size and timestamp questions
python3 ai_integration.py --filename hello_world.txt --query "what is the file size"
python3 ai_integration.py --filename hello_world.txt --query "when was it modified"

# Group questions
python3 ai_integration.py --filename hello_world.txt --query "what group owns this file"

# Complex natural language questions with search specifications
python3 ai_integration.py --filename hello_world.txt --query "explain the file permissions and what they mean"
python3 ai_integration.py --filename Hello_World.txt --query "find exact case-sensitive match and show all details"
python3 ai_integration.py --filename hello --query "find similar matches and explain their ownership"
```

## 📊 JSON Output Format

The enhanced C program outputs structured JSON with comprehensive file metadata:

```json
[
  {
    "name": "hello_world.txt",
    "path": "hello_world.txt",
    "size": 28,
    "owner": "john",
    "group": "users",
    "uid": 1000,
    "gid": 100,
    "permissions": "644",
    "permissions_readable": "-rw-r--r--",
    "type": "file",
    "modified": 1672531200,
    "accessed": 1672531200,
    "changed": 1672531200,
    "inode": 789012,
    "device": "16777234",
    "hard_links": 1,
    "block_size": 4096,
    "blocks": 8
  }
]
```

### Metadata Fields Explained

- **name**: Filename
- **path**: Full file path
- **size**: File size in bytes
- **owner**: Username of file owner
- **group**: Group name
- **uid/gid**: Numeric user and group IDs
- **permissions**: Octal permission notation (e.g., "644")
- **permissions_readable**: Human-readable format (e.g., "-rw-r--r--")
- **type**: File type (file, directory, symlink, char_device, block_device, fifo, socket)
- **modified/accessed/changed**: Unix timestamps
- **inode**: File system inode number
- **device**: Device identifier
- **hard_links**: Number of hard links
- **block_size/blocks**: File system block information

## 🧪 Testing

Run the comprehensive test suite:

```bash
python3 test_ai_integration.py
```

The test suite covers:
- JSON parsing and validation
- File search functionality with different match types
- AI question answering with mocked responses
- Error handling and fallback mechanisms
- Data formatting functions
- Exact matching functionality

## 🐳 Docker Support

### Build and Run with Docker

```bash
# Build the Docker image
docker build -t file-savant-ai .

# Run with environment file
docker run --rm -it \
  --env-file .env \
  -v $(pwd):/workspace \
  file-savant-ai --filename hello_world.txt --question "who owns hello_world.txt"
```

## 📁 Project Structure

```
FileSavantAI/
├── file_info.c              # Enhanced C program with JSON output
├── file_info                # Compiled C executable
├── ai_integration.py        # AI-powered Python analysis script
├── test_ai_integration.py   # Comprehensive test suite
├── hello_world.txt          # Test file
├── README.md               # Documentation
├── requirements.txt        # Python dependencies (openai, python-dotenv)
├── Dockerfile             # Docker configuration
├── rebuild_and_run.sh     # Automated Docker rebuild script
├── .env                   # Environment variables (not tracked)
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
└── sample_data/          # Sample test data directory
```

## 🔧 Command Line Options

```bash
python3 ai_integration.py [OPTIONS]

Options:
  --dir DIRECTORY          Directory to search (default: current)
  --filename FILENAME      Specific file to analyze
  --query QUERY            Natural language query about the file(s)
  --validate               Validate results with ls -l command
  --help                   Show help message

Important Notes:
- Use natural language to specify match types: "exact match", "case-sensitive", etc.
- AI requires OPENAI_API_KEY in .env file (fallback available)
```

## 🏗️ Architecture

### System Pipeline Overview

FileSavantAI combines C-level system operations with AI-powered analysis using Model Context Protocol (MCP) for efficient communication:

```mermaid
graph TD
    A["👤 User Natural Language Query<br/>with optional file targeting"] --> B["🔍 FileSavantAI MCP System"]
    
    B --> C["🔌 MCP Client (Python)<br/>Sends structured requests"]
    C --> D["⚙️ MCP Server (C)<br/>File system operations"]
    D --> E["📊 Structured Response<br/>File metadata via MCP protocol"]
    
    E --> F["🧠 AI Query Parser<br/>Extracts match type & case sensitivity"]
    F --> G["🎯 File Filtering<br/>Apply parsed parameters"]
    
    G --> H["🤖 AI Analysis<br/>GPT models understand natural queries"]
    H --> I{"🔑 API Available?"}
    
    I -->|"✅ Yes"| J["🧠 OpenAI Response<br/>Natural language answer"]
    I -->|"❌ No"| K["🔄 Fallback Analysis<br/>Keyword matching"]
    
    J --> L["✅ Validation<br/>Cross-check with ls -l"]
    K --> L
    
    L --> M["📋 Final Answer<br/>Intelligent file analysis"]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
    style E fill:#fff9c4
    style F fill:#fff9c4
    style H fill:#e8f5e8
    style J fill:#e8f5e8
    style K fill:#ffebee
    style M fill:#e1f5fe
```

### Core Features

**🎯 The MCP-based system has 6 main components:**

1. **🔌 MCP Communication Layer**: Efficient structured communication between Python client and C server

2. **⚙️ System-Level Data Collection**: C MCP server extracts complete file metadata (owner, permissions, timestamps)

3. **🧠 Natural Language Parsing**: AI extracts match specifications (exact, contains, similar, case-sensitive) from user queries

4. **🎯 Smart File Filtering**: Apply parsed parameters to target the right files

5. **🤖 AI-Powered Understanding**: OpenAI models interpret natural language queries about files

6. **🔄 Reliable Fallback**: Automatic keyword-based analysis when AI is unavailable with validation

### Two-Part Design (Task 2 Compliance)

1. **C MCP Server (`file_info_mcp_server.c`)**:
   - Implements Model Context Protocol server for file operations
   - Performs low-level file system operations using `stat()`, `readdir()`, etc.
   - Provides structured JSON responses via MCP protocol
   - Efficient system-level file analysis with error handling
   - Supports all major file types (files, directories, symlinks, devices, etc.)
   - Exposes tools: `list_files`, `get_file_info`, `search_files`

2. **AI-Powered Python MCP Client (`ai_integration.py`)**:
   - Uses OpenAI GPT-3.5-turbo for intelligent query answering
   - Communicates with C server via fast MCP protocol
   - Parses natural language for match specifications (exact, contains, similar, case-sensitive)
   - Converts file metadata into natural language responses
   - Handles complex queries beyond simple keyword matching
   - Includes automatic fallback analysis when AI is unavailable
   - Validates results using `ls -l` for accuracy
   - Hybrid approach: explicit arguments for core functionality, natural language for specifications

### 📊 Technical Implementation Details

#### C MCP Server Implementation
- **MCP Protocol**: Implements JSON-RPC 2.0 over stdin/stdout for structured communication
- **File system operations**: Uses `stat()`, `readdir()`, `lstat()` for complete metadata
- **Tool exposure**: `list_files`, `get_file_info`, `search_files` via MCP interface
- **Error handling**: Robust error checking for file access, permissions, and invalid paths
- **Memory management**: Proper cleanup of allocated memory and directory handles
- **Performance**: Efficient single-pass directory traversal with minimal protocol overhead

#### Python MCP Client Integration
- **MCP Communication**: Fast JSON-RPC communication with C server via pipes
- **AI query processing**: OpenAI API integration with structured prompt engineering
- **Hybrid parameter parsing**: Combines explicit CLI arguments with AI-extracted specifications
- **File filtering**: Multiple match types (exact, contains, similar) with case sensitivity options
- **Fallback system**: Graceful degradation when AI is unavailable, maintaining core functionality
- **Data validation**: Cross-reference with system tools (`ls -l`) for accuracy verification
- **Protocol efficiency**: Simplified MCP implementation for optimal speed

### How the C MCP Server Works

The core logic of the MCP server implements the JSON-RPC 2.0 protocol:

```c
// 1. MCP Server Loop
while (fgets(buffer, sizeof(buffer), stdin)) {
    // Parse JSON-RPC request
    cJSON *request = cJSON_Parse(buffer);
    
    // Handle method calls
    if (strcmp(method, "tools/call") == 0) {
        // Extract tool name from parameters
        if (strcmp(tool_name, "list_files") == 0) {
            list_files_handler(directory, request_id);
        }
        else if (strcmp(tool_name, "get_file_info") == 0) {
            get_file_info_handler(filename, request_id);
        }
    }
}

// 2. File Processing (list_files example)
static void list_files_handler(const char *directory, int id) {
    DIR *dir = opendir(directory);
    cJSON *files_array = cJSON_CreateArray();
    
    while ((entry = readdir(dir))) {
        if (entry->d_name[0] == '.') continue;  // Skip hidden files
        
        // Get file stats and create JSON object
        cJSON *file_obj = create_file_json(entry, &st);
        cJSON_AddItemToArray(files_array, file_obj);
    }
    
    // Send MCP response
    send_mcp_response(id, files_array);
}
```

**Simple Summary:**
- **Input:** MCP JSON-RPC requests via stdin
- **Process:** Parse requests → Execute file operations → Build responses
- **Output:** Structured MCP responses with file data

**For each file, it outputs:**
- ✅ Name and full path
- ✅ Size in bytes  
- ✅ Owner and group (both name and ID)
- ✅ Permissions (both octal `644` and readable `-rw-r--r--`)
- ✅ File type (file, directory, symlink, char_device, block_device, fifo, socket)
- ✅ Timestamps (modified, accessed, changed)
- ✅ System info (inode, device, hard links, blocks)

### Data Flow

The hybrid system implements a robust pipeline with natural language parsing and fallback mechanisms:

```
User Query → Argument Parsing → C Program Execution → JSON Processing → AI Query Parsing → File Filtering → AI Analysis → Validation → Output
```

**Key Pipeline Features:**
- **🧠 Natural Language Processing**: Extracts match specifications from user queries
- **🔄 Error Recovery**: Automatic fallback when AI is unavailable
- **🎯 Smart Filtering**: AI-parsed search strategies (exact, contains, similar, case-sensitive)
- **✅ Validation**: Cross-checking with system commands
- **🤖 AI Flexibility**: Configurable model selection
- **📊 Rich Metadata**: Comprehensive file information extraction
- **⚡ Hybrid Efficiency**: Core functionality through arguments, specifications through natural language

## 📋 Examples

### 🔧 Running the C Program Directly

The C program can be used standalone to get JSON file information:

```bash
# Compile the C program
gcc -o file_info file_info.c

# Run on current directory
./file_info
# Output: JSON array with all files in current directory

# Run on specific directory
./file_info /usr/local
# Output: JSON array with files in /usr/local

# Example output for current directory:
[
{
  "name": "hello_world.txt",
  "path": "hello_world.txt",
  "size": 28,
  "owner": "msalah",
  "group": "staff",
  "uid": 501,
  "gid": 20,
  "permissions": "644",
  "permissions_readable": "-rw-r--r--",
  "type": "file",
  "modified": 1749568445,
  "accessed": 1749599718,
  "changed": 1749568445,
  "inode": 204567456,
  "device": "16777234",
  "hard_links": 1,
  "block_size": 4096,
  "blocks": 8
}
]

# Test JSON validity
./file_info . | python3 -m json.tool
# If valid JSON, it will be pretty-printed

# Error handling example
./file_info /nonexistent/directory
# Output: {"error": "Cannot open directory", "directory": "/nonexistent/directory"}
```

### 🐍 Python AI Integration Examples

Complete examples of using the AI-powered analysis:

```bash
# Basic ownership query
python3 ai_integration.py --filename hello_world.txt --query "who owns this file"
# Output: 🤖 AI Analysis: The file hello_world.txt is owned by msalah (UID: 501)

# Permission analysis
python3 ai_integration.py --filename hello_world.txt --query "what are the permissions"
# Output: 🤖 AI Analysis: The file has permissions -rw-r--r-- (644), meaning owner can read/write, group and others can only read

# File size information
python3 ai_integration.py --filename hello_world.txt --query "what is the file size"
# Output: 🤖 AI Analysis: The file hello_world.txt is 28.0 B in size

# Group ownership
python3 ai_integration.py --filename hello_world.txt --query "what group owns this file"
# Output: 🤖 AI Analysis: The file is owned by the staff group (GID: 20)

# Comprehensive file analysis with natural language specifications
python3 ai_integration.py --filename hello_world.txt --query "show exact match with all details"
# Output: Complete file details with emojis and formatted information

# Search with validation
python3 ai_integration.py --filename hello_world.txt --query "who owns this file" --validate
# Output: AI analysis + ls -l validation

# Natural language match type specifications
python3 ai_integration.py --filename world --query "find files containing this name"
python3 ai_integration.py --filename hello_world.txt --query "show exact match with details"
python3 ai_integration.py --filename hello --query "find similar matches and show ownership"

# Case-sensitive search with natural language
python3 ai_integration.py --filename Hello_World.txt --query "find case-sensitive exact match"

# Search in specific directory
python3 ai_integration.py --dir /usr/local --filename bin --query "who owns this file"

# Testing exact match functionality with hybrid model
python3 ai_integration.py --filename hello_worl --query "show exact match"
# Output: ❌ File 'hello_worl' not found. (correctly returns not found)
```

### 🐳 Docker Examples

Run the entire system in a containerized environment:

```bash
# Build the Docker image
docker build -t file-savant-ai .

# Basic Docker run
docker run --rm -it file-savant-ai --filename hello_world.txt --query "who owns this file"

# With environment file and volume mounting
docker run --rm -it \
  --env-file .env \
  -v $(pwd)/sample_data:/data \
  file-savant-ai --filename hello_world.txt --query "show me all details"

# Analyze files in mounted directory
docker run --rm -it \
  -v $(pwd):/workspace \
  file-savant-ai --dir /workspace --filename README.md --query "what are the permissions"

# Interactive mode with detailed file listing
docker run --rm -it \
  --env-file .env \
  file-savant-ai --query "list all files with detailed information"
```

### 🔄 Shell Script Examples

Use the automated rebuild and run script:

```bash
# Make script executable
chmod +x rebuild_and_run.sh

# Basic usage - rebuilds image and runs with arguments
./rebuild_and_run.sh --filename hello_world.txt --query "who owns this file"

# List all files in container with details
./rebuild_and_run.sh --query "list all files with their detailed information"

# Ownership query with validation
./rebuild_and_run.sh --filename hello_world.txt --query "who owns this file" --validate

# Permission analysis
./rebuild_and_run.sh --filename hello_world.txt --query "what are the permissions"
```

### 🔍 Complete Workflow Example

Here's a complete example showing all components working together:

```bash
# Step 1: Compile C program
gcc -o file_info file_info.c

# Step 2: Test C program directly
./file_info .

# Step 3: Use Python AI integration with hybrid model
python3 ai_integration.py --filename hello_world.txt --query "who owns this file" --validate

# Step 4: Docker containerized version
docker build -t file-savant-ai .
docker run --rm -it file-savant-ai --filename hello_world.txt --query "who owns this file"

# Step 5: Automated rebuild and run
./rebuild_and_run.sh --filename hello_world.txt --query "who owns this file"
```

## 🔍 Task 2 Validation Example

The system perfectly meets Task 2 requirements by providing real AI integration:

```bash
# Ask AI about file ownership with validation using hybrid model
python3 ai_integration.py --filename hello_world.txt --query "who owns this file" --validate

# Expected Output:
🔍 Analyzing files in '.'...
✅ Found 12 files

🤖 AI Analysis for 'hello_world.txt':
🤖 AI Analysis:
The file hello_world.txt is owned by msalah (UID: 501). This user has read and write permissions on the file, while the group (staff, GID: 20) and other users have read-only access.

🔎 Validation with 'ls -l':
  hello_world.txt:
    -rw-r--r--@ 1 msalah  staff  28 Jun 10 18:14 hello_world.txt
```

## 📄 License

This project is open source and available under the MIT License.
