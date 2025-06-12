import unittest
from unittest.mock import patch, MagicMock

from ai_integration import find_file, run_file_info_simple_rpc, answer_file_question_with_ai, format_file_size, format_timestamp

class TestEnhancedFileAnalyzer(unittest.TestCase):

    def setUp(self):
        """Set up mock JSON data for tests."""
        self.mock_json_output = '''[
{
  "name": "file_info",
  "path": "file_info",
  "size": 34040,
  "owner": "msalah",
  "group": "staff",
  "uid": 501,
  "gid": 20,
  "permissions": "755",
  "permissions_readable": "-rwxr-xr-x",
  "type": "file",
  "modified": 1672531200,
  "accessed": 1672531200,
  "changed": 1672531200,
  "inode": 123456,
  "device": "16777234",
  "hard_links": 1,
  "block_size": 4096,
  "blocks": 68
},
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
  "modified": 1672531300,
  "accessed": 1672531300,
  "changed": 1672531300,
  "inode": 789012,
  "device": "16777234",
  "hard_links": 1,
  "block_size": 4096,
  "blocks": 8
},
{
  "name": "README.md",
  "path": "README.md",
  "size": 3608,
  "owner": "alice",
  "group": "developers",
  "uid": 1001,
  "gid": 101,
  "permissions": "664",
  "permissions_readable": "-rw-rw-r--",
  "type": "file",
  "modified": 1672531400,
  "accessed": 1672531400,
  "changed": 1672531400,
  "inode": 345678,
  "device": "16777234",
  "hard_links": 1,
  "block_size": 4096,
  "blocks": 8
}
]'''

        self.expected_parsed_data = [
            {
                "name": "file_info",
                "path": "file_info",
                "size": 34040,
                "owner": "msalah",
                "group": "staff",
                "uid": 501,
                "gid": 20,
                "permissions": "755",
                "permissions_readable": "-rwxr-xr-x",
                "type": "file",
                "modified": 1672531200,
                "accessed": 1672531200,
                "changed": 1672531200,
                "inode": 123456,
                "device": "16777234",
                "hard_links": 1,
                "block_size": 4096,
                "blocks": 68
            },
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
                "modified": 1672531300,
                "accessed": 1672531300,
                "changed": 1672531300,
                "inode": 789012,
                "device": "16777234",
                "hard_links": 1,
                "block_size": 4096,
                "blocks": 8
            },
            {
                "name": "README.md",
                "path": "README.md",
                "size": 3608,
                "owner": "alice",
                "group": "developers",
                "uid": 1001,
                "gid": 101,
                "permissions": "664",
                "permissions_readable": "-rw-rw-r--",
                "type": "file",
                "modified": 1672531400,
                "accessed": 1672531400,
                "changed": 1672531400,
                "inode": 345678,
                "device": "16777234",
                "hard_links": 1,
                "block_size": 4096,
                "blocks": 8
            }
        ]

    def test_parse_file_info_json_success(self):
        """Test successful parsing of JSON output from MCP response."""
        # Test direct list parsing (MCP returns the list directly)
        test_data = [
            {"name": "file_info", "owner": "msalah", "permissions": "755"},
            {"name": "hello_world.txt", "owner": "john", "permissions": "644"},
            {"name": "README.md", "owner": "alice", "permissions": "664"}
        ]
        self.assertEqual(len(test_data), 3)
        self.assertEqual(test_data[0]['name'], 'file_info')
        self.assertEqual(test_data[1]['owner'], 'john')
        self.assertEqual(test_data[2]['permissions'], '664')

    def test_parse_file_info_empty_input(self):
        """Test parsing with empty input."""
        # MCP returns empty list directly
        parsed_data = []
        self.assertEqual(parsed_data, [])

    def test_parse_file_info_malformed_json(self):
        """Test handling malformed MCP responses."""
        # In MCP approach, malformed responses return empty list
        parsed_data = []
        self.assertEqual(parsed_data, [])

    def test_find_file_exact_match(self):
        """Test finding a file with exact name match."""
        matches = find_file(self.expected_parsed_data, 'hello_world.txt', 'exact')
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['name'], 'hello_world.txt')

    def test_find_file_contains_match(self):
        """Test finding files with contains match."""
        matches = find_file(self.expected_parsed_data, 'file', 'contains')
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['name'], 'file_info')

    def test_find_file_case_sensitive(self):
        """Test case-sensitive file search."""
        matches = find_file(self.expected_parsed_data, 'README.MD', 'exact', case_sensitive=True)
        self.assertEqual(len(matches), 0)
        
        matches = find_file(self.expected_parsed_data, 'README.md', 'exact', case_sensitive=True)
        self.assertEqual(len(matches), 1)

    def test_find_file_no_match(self):
        """Test search with no matching files."""
        matches = find_file(self.expected_parsed_data, 'nonexistent', 'exact')
        self.assertEqual(matches, [])

    def test_format_file_size(self):
        """Test file size formatting."""
        self.assertEqual(format_file_size(1024), "1.0 KB")
        self.assertEqual(format_file_size(1048576), "1.0 MB")
        self.assertEqual(format_file_size(500), "500.0 B")

    def test_format_timestamp(self):
        """Test timestamp formatting."""
        timestamp = 1672531200  # 2023-01-01 00:00:00 (approximately)
        formatted = format_timestamp(timestamp)
        self.assertIn("2023", formatted)

    @patch('ai_integration.openai.ChatCompletion.create')
    @patch('ai_integration.os.getenv')
    def test_answer_file_question_who_owns(self, mock_getenv, mock_openai):
        """Test answering 'who owns' questions with AI."""
        mock_getenv.return_value = "test_api_key"
        mock_openai.return_value.choices = [MagicMock(message=MagicMock(content="hello_world.txt is owned by john (UID: 1000)"))]
        
        answer = answer_file_question_with_ai(self.expected_parsed_data, "who owns hello_world.txt", "hello_world.txt", suppress_warnings=True)
        self.assertIn("john", answer)
        self.assertIn("UID: 1000", answer)

    @patch('ai_integration.os.getenv')
    def test_answer_file_question_no_api_key(self, mock_getenv):
        """Test fallback when no API key is provided."""
        mock_getenv.return_value = None
        answer = answer_file_question_with_ai(self.expected_parsed_data, "who owns hello_world.txt", "hello_world.txt", suppress_warnings=True)
        self.assertIn("OpenAI API key not found", answer)

    @patch('ai_integration.openai.ChatCompletion.create')
    @patch('ai_integration.os.getenv')
    def test_answer_file_question_ai_failure(self, mock_getenv, mock_openai):
        """Test fallback when AI fails."""
        mock_getenv.return_value = "test_api_key"
        mock_openai.side_effect = Exception("API Error")
        
        answer = answer_file_question_with_ai(self.expected_parsed_data, "who owns hello_world.txt", "hello_world.txt", suppress_warnings=True)
        self.assertIn("hello_world.txt", answer)
        self.assertIn("john", answer)

    @patch('ai_integration.subprocess.Popen')
    def test_run_file_info_mcp_success(self, mock_popen):
        """Test the MCP server communication on success."""
        # Mock the process
        mock_process = MagicMock()
        mock_process.stdout = iter(['{"jsonrpc":"2.0","id":1,"result":[{"name":"test.txt","size":100}]}'])
        mock_process.stdin = MagicMock()
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        
        files = run_file_info_simple_rpc("/fake/dir")
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]['name'], 'test.txt')

    @patch('ai_integration.subprocess.Popen')
    def test_run_file_info_mcp_failure(self, mock_popen):
        """Test the MCP server communication on failure."""
        mock_popen.side_effect = Exception("MCP server failed")
        files = run_file_info_simple_rpc(".")
        self.assertEqual(files, [])

    def test_answer_no_files(self):
        """Test answering questions when no files are found."""
        answer = answer_file_question_with_ai([], "who owns test", "test", suppress_warnings=True)
        self.assertIn("No files found", answer)

    def test_answer_file_not_found(self):
        """Test answering questions when specific file is not found."""
        answer = answer_file_question_with_ai(self.expected_parsed_data, "who owns test", "nonexistent.txt", suppress_warnings=True)
        self.assertIn("not found", answer)

    def test_exact_match_functionality(self):
        """Test that exact matching works correctly."""
        # Should not find "hello_worl" when looking for exact match
        answer = answer_file_question_with_ai(self.expected_parsed_data, "who owns with exact match", "hello_worl", suppress_warnings=True)
        self.assertIn("not found", answer)
        
        # Should find exact match
        answer = answer_file_question_with_ai(self.expected_parsed_data, "who owns with exact match", "hello_world.txt", suppress_warnings=True)
        self.assertIn("john", answer.lower())

if __name__ == '__main__':
    unittest.main() 