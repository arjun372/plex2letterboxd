from plexapi.server import PlexServer
from plexapi.myplex import MyPlexAccount
import unittest
from unittest.mock import patch
from plex2letterboxd.plex2letterboxd import setup_plex_server


class TestSetupPlexServer(unittest.TestCase):

    @patch.object(PlexServer, '__init__', side_effect=Exception('Failed to connect'))  # Mock PlexServer to raise an exception
    def test_setup_plex_server_fail_to_connect(self, mock_plexserver):
        with self.assertRaises(SystemExit):
            setup_plex_server({'baseurl': 'http://localhost', 'token': '12345'}, 'managed_user')

    @patch.object(PlexServer, '__init__', return_value=None)  # Mock PlexServer
    @patch.object(MyPlexAccount, '__init__', return_value=None)  # Mock MyPlexAccount
    @patch.object(MyPlexAccount, 'user', side_effect=Exception('Failed to setup'))  # Mock user method to raise an exception
    def test_setup_plex_server_fail_to_setup(self, mock_user, mock_myplexaccount, mock_plexserver):
        with self.assertRaises(SystemExit):
            setup_plex_server({'baseurl': 'http://localhost', 'token': '12345'}, 'managed_user')