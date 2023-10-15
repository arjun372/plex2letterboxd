import argparse
import configparser
import csv
import sys
import logging
from urllib.parse import urlparse
from plexapi.myplex import MyPlexUser, MyPlexAccount
from plexapi.server import PlexServer
from typing import List, Any, Optional
import concurrent.futures

# Constants
BASE_URL = 'baseurl'
TOKEN = 'token'
CONFIG_AUTH = 'auth'

# Set up logging
logging.basicConfig(level=logging.INFO)
logger: logging.Logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Namespace object with all arguments.
    """
    about: str = 'Export watched Plex movies to the Letterboxd import format.'
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description=about, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i', '--ini', default='config.ini', help='config file')
    parser.add_argument('-o', '--output', default='letterboxd.csv', help='file to output to')
    parser.add_argument('-s', '--sections', default=['Movies'], nargs='+', help='sections to grab from')
    parser.add_argument('-m', '--managed-user', help='name of managed user to export')
    return parser.parse_args()


def parse_config(ini: str) -> configparser.SectionProxy:
    """
    Parse the configuration file.

    Args:
        ini (str): The path to the configuration file.

    Returns:
        configparser.SectionProxy: The parsed configuration file.

    Raises:
        SystemExit: If the configuration file cannot be parsed or if required values are missing.
    """
    config: configparser.ConfigParser = configparser.ConfigParser()
    try:
        config.read(ini)
    except configparser.Error as e:
        logger.error(f"Failed to parse config file: {e}")
        sys.exit(1)

    auth: configparser.SectionProxy = config[CONFIG_AUTH]
    missing: set = {BASE_URL, TOKEN} - set(auth.keys())
    if missing:
        logger.error(f"Missing the following config values: {missing}")
        sys.exit(1)

    # Validate base URL
    try:
        result: urlparse.ParseResult = urlparse(auth[BASE_URL])
        if not all([result.scheme, result.netloc]):
            raise ValueError("Base URL is not valid")
    except ValueError as e:
        logger.error(f"Invalid base URL: {e}")
        sys.exit(1)
    return auth


def fetch_movie_details(movie: Any) -> List[Any]:
    """
    Fetch details of a movie.

    Args:
        movie (Any): The movie object.

    Returns:
        List[Any]: A list containing movie title, year, rating and date.
    """
    date: Optional[str] = None
    if movie.lastViewedAt is not None:
        date = movie.lastViewedAt.strftime('%Y-%m-%d')
    rating: Optional[str] = movie.userRating
    if rating is not None:
        rating = f'{movie.userRating:.0f}'
    print(movie.title, movie.year, rating, date)
    return [movie.title, movie.year, rating, date]


def fetch_section_details(sections: List[Any], max_workers: Optional[int] = 10) -> List[List[Any]]:
    """
    Fetch details of all movies in the given sections.

    Args:
        sections (List[Any]): A list of section objects.
        max_workers (Optional[int]): The maximum number of threads that can be used to execute the given calls.
        Defaults to None.

    Returns:
        List[List[Any]]: A list of lists containing details of all movies.
    """
    all_movie_details: List[List[Any]] = []
    for section in sections:
        found_movies: List[Any] = section.search(sort='lastViewedAt', unwatched=False)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            movie_details: List[List[Any]] = list(executor.map(fetch_movie_details, found_movies))
            all_movie_details.extend(movie_details)
    return all_movie_details


def setup_plex_server(auth: configparser.SectionProxy, managed_user: Optional[str] = None) -> PlexServer:
    """
    Set up the Plex server.

    Args:
        auth (configparser.SectionProxy): The parsed configuration file.
        managed_user (Optional[str]): The name of the managed user. Defaults to None.

    Returns:
        PlexServer: The Plex server object.

    Raises:
        SystemExit: If the Plex server cannot be connected or if the managed user cannot be setup.
    """
    try:
        plex: PlexServer = PlexServer(auth[BASE_URL], auth[TOKEN])
    except Exception as e:
        logger.error(f"Failed to connect to Plex server: {e}")
        sys.exit(1)

    if managed_user:
        try:
            myplex: MyPlexAccount = plex.myPlexAccount()
            user: MyPlexUser = myplex.user(managed_user)
            token: str = user.get_token(plex.machineIdentifier)
            plex = PlexServer(auth[BASE_URL], token)
        except Exception as e:
            logger.error(f"Failed to setup managed user: {e}")
            sys.exit(1)

    return plex


def write_csv(sections: List[Any], output: str) -> None:
    """
    Write movie details to a CSV file.

    Args:
        sections (List[Any]): A list of section objects.
        output (str): The path to the output file.
    """
    with open(output, 'w', newline='') as f:
        writer: csv.writer = csv.writer(f)
        all_movie_details: List[List[Any]] = [['Title', 'Year', 'Rating10', 'WatchedDate']]
        all_movie_details.extend(fetch_section_details(sections))
        writer.writerows(all_movie_details)


def main() -> None:
    """
    The main function of the script.
    """
    args: argparse.Namespace = parse_args()
    auth: configparser.SectionProxy = parse_config(args.ini)
    plex: PlexServer = setup_plex_server(auth, args.managed_user)
    sections: List[Any] = [plex.library.section(s) for s in args.sections]
    write_csv(sections, args.output)
