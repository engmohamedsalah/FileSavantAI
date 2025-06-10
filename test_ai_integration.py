import unittest
from unittest.mock import patch, MagicMock
import io
import contextlib

# Import the functions from the main script
from ai_integration import parse_file_info, get_specific_file_info, run_file_info, analyze_with_ai

class TestFileSavantAI(unittest.TestCase):

    def setUp(self):
        """Set up mock data for tests."""
        self.mock_c_output = """755 1 msalah staff 34040 Jun 10 18:32 file_info
644 1 msalah staff 1130 Jun 10 18:32 file_info.c
644 1 msalah staff 3608 Jun 10 19:01 README.md
644 1 msalah staff 28 Jun 10 18:14 hello_world.txt
"""
        self.mock_files_data = [
            {'permissions': '755', 'links': '1', 'owner': 'msalah', 'group': 'staff', 'size': '34040', 'date': 'Jun 10', 'time': '18:32', 'name': 'file_info'},
            {'permissions': '644', 'links': '1', 'owner': 'msalah', 'group': 'staff', 'size': '1130', 'date': 'Jun 10', 'time': '18:32', 'name': 'file_info.c'},
            {'permissions': '644', 'links': '1', 'owner': 'msalah', 'group': 'staff', 'size': '3608', 'date': 'Jun 10', 'time': '19:01', 'name': 'README.md'},
            {'permissions': '644', 'links': '1', 'owner': 'msalah', 'group': 'staff', 'size': '28', 'date': 'Jun 10', 'time': '18:14', 'name': 'hello_world.txt'}
        ]

    def test_parse_file_info_success(self):
        """Test successful parsing of C program output."""
        parsed_data = parse_file_info(self.mock_c_output)
        self.assertEqual(len(parsed_data), 4)
        self.assertEqual(parsed_data[0]['name'], 'file_info')
        self.assertEqual(parsed_data[3]['name'], 'hello_world.txt')

    def test_parse_file_info_empty_input(self):
        """Test parsing with empty input."""
        parsed_data = parse_file_info("")
        self.assertEqual(parsed_data, [])

    # --- Tests for get_specific_file_info ---

    def test_exact_match_case_insensitive(self):
        """Test exact match, case-insensitive (default)."""
        with io.StringIO() as buf, contextlib.redirect_stdout(buf):
            get_specific_file_info(self.mock_files_data, 'readme.md')
            output = buf.getvalue()
        self.assertIn("File: README.md", output)
        self.assertIn("Found 1 matching file(s)", output)

    def test_exact_match_case_sensitive_success(self):
        """Test exact match, case-sensitive, successful find."""
        with io.StringIO() as buf, contextlib.redirect_stdout(buf):
            get_specific_file_info(self.mock_files_data, 'README.md', case_sensitive=True)
            output = buf.getvalue()
        self.assertIn("File: README.md", output)

    def test_exact_match_case_sensitive_fail(self):
        """Test exact match, case-sensitive, failure to find."""
        with io.StringIO() as buf, contextlib.redirect_stdout(buf):
            get_specific_file_info(self.mock_files_data, 'readme.md', case_sensitive=True)
            output = buf.getvalue()
        self.assertIn("No files found", output)

    def test_contains_match(self):
        """Test 'contains' match type."""
        with io.StringIO() as buf, contextlib.redirect_stdout(buf):
            get_specific_file_info(self.mock_files_data, 'info', match_type='contains')
            output = buf.getvalue()
        self.assertIn("Found 2 matching file(s)", output)
        self.assertIn("File: file_info", output)
        self.assertIn("File: file_info.c", output)
        
    def test_similar_match(self):
        """Test 'similar' match type."""
        with io.StringIO() as buf, contextlib.redirect_stdout(buf):
            get_specific_file_info(self.mock_files_data, 'readm.md', match_type='similar')
            output = buf.getvalue()
        self.assertIn("Did you mean one of these?", output)
        self.assertIn("File: README.md", output)

    def test_no_match_found(self):
        """Test when no file matches any criteria."""
        with io.StringIO() as buf, contextlib.redirect_stdout(buf):
            get_specific_file_info(self.mock_files_data, 'nonexistentfile.xyz', match_type='exact')
            output = buf.getvalue()
        self.assertIn("No files found", output)

    # --- Tests with Mocks ---
    
    @patch('ai_integration.subprocess.run')
    def test_run_file_info(self, mock_subprocess_run):
        """Test the C program runner function, mocking the subprocess."""
        mock_subprocess_run.return_value = MagicMock(stdout=self.mock_c_output, returncode=0, check_returncode=lambda: None)
        output = run_file_info()
        self.assertEqual(output, self.mock_c_output)

    @patch('ai_integration.openai.ChatCompletion.create')
    def test_analyze_with_ai(self, mock_openai_create):
        """Test the AI analysis function, mocking the OpenAI API call."""
        mock_openai_create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content="AI Summary"))])
        summary = analyze_with_ai(self.mock_files_data)
        self.assertEqual(summary, "AI Summary")
        mock_openai_create.assert_called_once()

if __name__ == '__main__':
    unittest.main() 