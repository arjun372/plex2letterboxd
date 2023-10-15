import unittest
from unittest.mock import patch, MagicMock
from plex2letterboxd.plex2letterboxd import parse_args, parse_config, fetch_section_details


class TestPlex2Letterboxd(unittest.TestCase):

    @patch('argparse.ArgumentParser.parse_args')
    def test_parse_args(self, mock_parse_args):
        parse_args()
        mock_parse_args.assert_called_once()

    @patch('configparser.ConfigParser')
    def test_parse_config(self, mock_config_parser):
        mock_config = mock_config_parser.return_value
        mock_config.read.return_value = None
        mock_config.__getitem__.return_value = {'baseurl': 'http://localhost', 'token': '12345'}
        result = parse_config('config.ini')
        self.assertEqual(result, {'baseurl': 'http://localhost', 'token': '12345'})

    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_fetch_section_details(self, mock_executor):
        mock_section = MagicMock()
        mock_movie = MagicMock()
        mock_section.search.return_value = [mock_movie]
        mock_executor.return_value.__enter__.return_value.map.return_value = [['Test Movie', 2020, '7', None]]
        result = fetch_section_details([mock_section])
        self.assertEqual(len(result), 1)
        self.assertEqual(result, [['Test Movie', 2020, '7', None]])

    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_fetch_section_details_multiple_sections(self, mock_executor):
        mock_section1 = MagicMock()
        mock_section2 = MagicMock()
        mock_movie1 = MagicMock()
        mock_movie2 = MagicMock()
        mock_section1.search.return_value = [mock_movie1]
        mock_section2.search.return_value = [mock_movie2]
        mock_executor.return_value.__enter__.return_value.map.side_effect = [
            [['Test Movie 1', 2020, '7', None]],
            [['Test Movie 2', 2021, '8', None]]
        ]
        result = fetch_section_details([mock_section1, mock_section2])
        self.assertEqual(result, [['Test Movie 1', 2020, '7', None], ['Test Movie 2', 2021, '8', None]])

    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_fetch_section_details_no_movies(self, mock_executor):
        mock_section = MagicMock()
        mock_section.search.return_value = []
        result = fetch_section_details([mock_section])
        self.assertEqual(result, [])

    def test_parse_config_missing_values(self):
        mock_config = MagicMock()
        mock_config.__getitem__.return_value = {'token': 'test'}  # baseurl is missing
        with patch('configparser.ConfigParser', return_value=mock_config):
            with self.assertRaises(SystemExit):
                parse_config('test.ini')

    def test_parse_config_invalid_url(self):
        mock_config = MagicMock()
        mock_config.__getitem__.return_value = {'baseurl': 'invalid', 'token': 'test'}
        with patch('configparser.ConfigParser', return_value=mock_config):
            with self.assertRaises(SystemExit):
                parse_config('test.ini')


if __name__ == '__main__':
    unittest.main()