import unittest
from unittest.mock import patch, MagicMock
from plex2letterboxd.plex2letterboxd import write_csv


class TestWriteCsv(unittest.TestCase):

    @patch('builtins.open')
    @patch('csv.writer')
    @patch('plex2letterboxd.plex2letterboxd.fetch_section_details')
    def test_write_csv(self, mock_fetch_section_details, mock_csv_writer, mock_open):
        mock_section = MagicMock()
        mock_fetch_section_details.return_value = [['Test Movie', 2020, '7', None]]
        write_csv([mock_section], 'output.csv')
        mock_open.assert_called_once_with('output.csv', 'w', newline='')
        self.assertEqual(mock_csv_writer.return_value.writerows.call_count, 1)

    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('csv.writer')
    @patch('plex2letterboxd.plex2letterboxd.fetch_section_details')
    def test_write_csv_success(self, mock_fetch_section_details, mock_csv_writer, mock_open):
        mock_section = MagicMock()
        mock_fetch_section_details.return_value = [['Test Movie', 2020, '7', '2021-01-01']]
        write_csv([mock_section], 'output.csv')
        mock_open.assert_called_once_with('output.csv', 'w', newline='')
        mock_csv_writer.assert_called_once_with(mock_open())
        mock_csv_writer.return_value.writerows.assert_called_once_with(
            [['Title', 'Year', 'Rating10', 'WatchedDate'], ['Test Movie', 2020, '7', '2021-01-01']])

    @patch('builtins.open', side_effect=PermissionError)
    @patch('csv.writer')
    @patch('plex2letterboxd.plex2letterboxd.fetch_section_details')
    def test_write_csv_permission_error(self, mock_fetch_section_details, mock_csv_writer, mock_open):
        mock_section = MagicMock()
        mock_fetch_section_details.return_value = [['Test Movie', 2020, '7', '2021-01-01']]
        with self.assertRaises(PermissionError):
            write_csv([mock_section], 'output.csv')

    @patch('builtins.open', side_effect=IOError)
    @patch('csv.writer')
    @patch('plex2letterboxd.plex2letterboxd.fetch_section_details')
    def test_write_csv_io_error(self, mock_fetch_section_details, mock_csv_writer, mock_open):
        mock_section = MagicMock()
        mock_fetch_section_details.return_value = [['Test Movie', 2020, '7', '2021-01-01']]
        with self.assertRaises(IOError):
            write_csv([mock_section], 'output.csv')



if __name__ == '__main__':
    unittest.main()