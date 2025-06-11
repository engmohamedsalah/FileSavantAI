import unittest
from unittest.mock import patch, MagicMock
import io
import sys
from contextlib import redirect_stdout
from ai_integration import parse_file_info, find_file, run_file_info, main

class TestSimpleFileAnalyzer(unittest.TestCase):

    def setUp(self):
        """Set up mock data for tests."""
        self.mock_c_output = """34040 bytes file_info
1130 bytes file_info.c
3608 bytes README.md
28 bytes hello_world.txt
120 bytes another file with spaces.log
"""
        self.mock_parsed_data = [
            {'size': '34040', 'name': 'file_info'},
            {'size': '1130', 'name': 'file_info.c'},
            {'size': '3608', 'name': 'README.md'},
            {'size': '28', 'name': 'hello_world.txt'},
            {'size': '120', 'name': 'another file with spaces.log'}
        ]

    def test_parse_file_info_success(self):
        """Test successful parsing of the simplified C program output."""
        parsed_data = parse_file_info(self.mock_c_output)
        self.assertEqual(parsed_data, self.mock_parsed_data)

    def test_parse_file_info_empty_input(self):
        """Test parsing with empty input."""
        parsed_data = parse_file_info("")
        self.assertEqual(parsed_data, [])

    def test_parse_file_info_malformed_line(self):
        """Test parsing with a malformed line that should be ignored."""
        malformed_output = "this is not valid output\n" + self.mock_c_output
        parsed_data = parse_file_info(malformed_output)
        self.assertEqual(parsed_data, self.mock_parsed_data)

    def test_find_file_exact_match(self):
        """Test finding a file with an exact name match (case-insensitive)."""
        matches = find_file(self.mock_parsed_data, 'readme.md')
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['name'], 'README.md')

    def test_find_file_partial_match(self):
        """Test finding files with a partial name match."""
        matches = find_file(self.mock_parsed_data, 'info')
        self.assertEqual(len(matches), 2)
        self.assertIn('file_info', [m['name'] for m in matches])
        self.assertIn('file_info.c', [m['name'] for m in matches])
        
    def test_find_file_with_spaces(self):
        """Test finding a file that has spaces in its name."""
        matches = find_file(self.mock_parsed_data, 'file with spaces')
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['name'], 'another file with spaces.log')

    def test_find_file_no_match(self):
        """Test search with no matching files."""
        matches = find_file(self.mock_parsed_data, 'nonexistent')
        self.assertEqual(matches, [])

    @patch('ai_integration.subprocess.run')
    def test_run_file_info_success(self, mock_subprocess_run):
        """Test the C program runner on success."""
        mock_subprocess_run.return_value = MagicMock(stdout=self.mock_c_output, check_returncode=lambda: None)
        output = run_file_info(directory="/fake/dir")
        self.assertEqual(output, self.mock_c_output)
        # Check that it was called correctly
        mock_subprocess_run.assert_called_once_with(
            ['./file_info', '/fake/dir'],
            capture_output=True,
            text=True,
            check=True
        )
    
    @patch('ai_integration.subprocess.run')
    def test_run_file_info_failure(self, mock_subprocess_run):
        """Test the C program runner on failure."""
        mock_subprocess_run.side_effect = Exception("C program failed")
        output = run_file_info(directory=".")
        self.assertIsNone(output)

    @patch('ai_integration.run_file_info')
    def test_main_search_in_dir_success(self, mock_run_file_info):
        """Test main function for a successful search in a specified directory."""
        # Arrange
        test_args = ['ai_integration.py', 'hello', '--dir', '/test/dir']
        mock_run_file_info.return_value = self.mock_c_output
        
        # Act
        with patch.object(sys, 'argv', test_args), \
             io.StringIO() as buf, \
             redirect_stdout(buf):
            main()
            output = buf.getvalue()
            
        # Assert
        mock_run_file_info.assert_called_once_with('/test/dir')
        self.assertIn("Found 1 matching file(s)", output)
        self.assertIn("hello_world.txt", output)

    @patch('ai_integration.run_file_info')
    def test_main_search_in_dir_fail(self, mock_run_file_info):
        """Test main function for a failed search in a specified directory."""
        # Arrange
        test_args = ['ai_integration.py', 'nonexistent', '--dir', '/test/dir']
        mock_run_file_info.return_value = self.mock_c_output
        
        # Act
        with patch.object(sys, 'argv', test_args), \
             io.StringIO() as buf, \
             redirect_stdout(buf):
            main()
            output = buf.getvalue()
            
        # Assert
        mock_run_file_info.assert_called_once_with('/test/dir')
        self.assertIn("No files found matching 'nonexistent'", output)

if __name__ == '__main__':
    unittest.main() 