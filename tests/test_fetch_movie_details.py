import unittest
from datetime import datetime
from unittest.mock import MagicMock
from plex2letterboxd.plex2letterboxd import fetch_movie_details


class TestFetchMovieDetails(unittest.TestCase):

    def test_fetch_movie_details(self):
        mock_movie = MagicMock()
        mock_movie.title = 'Test Movie'
        mock_movie.year = 2020
        mock_movie.userRating = 7
        mock_movie.lastViewedAt = None
        result = fetch_movie_details(mock_movie)
        self.assertEqual(result, ['Test Movie', 2020, '7', None])

    def test_fetch_movie_details_with_comma_in_title(self):
        mock_movie = MagicMock()
        mock_movie.title = 'Test, Movie'
        mock_movie.year = 2020
        mock_movie.userRating = 7
        mock_movie.lastViewedAt = None
        result = fetch_movie_details(mock_movie)
        self.assertEqual(result, ['"Test, Movie"', 2020, '7', None])

    def test_fetch_movie_details_with_date(self):
        mock_movie = MagicMock()
        mock_movie.title = 'Test Movie'
        mock_movie.year = 2020
        mock_movie.userRating = 7
        mock_movie.lastViewedAt = datetime(2021, 1, 1)
        result = fetch_movie_details(mock_movie)
        self.assertEqual(result, ['Test Movie', 2020, '7', '2021-01-01'])

    def test_fetch_movie_details_with_none_rating(self):
        mock_movie = MagicMock()
        mock_movie.title = 'Test Movie'
        mock_movie.year = 2020
        mock_movie.userRating = None
        mock_movie.lastViewedAt = None
        result = fetch_movie_details(mock_movie)
        self.assertEqual(result, ['Test Movie', 2020, None, None])


if __name__ == '__main__':
    unittest.main()