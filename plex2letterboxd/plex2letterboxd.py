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
from tqdm import tqdm

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

    This function takes a movie object as input and returns a list containing the movie's title, year, rating, and the
    date it was last viewed.

    The movie object is expected to have the following attributes:
    - title: The title of the movie.
    - year: The year the movie was released.
    - userRating: The user's rating of the movie.
    - lastViewedAt: The date the movie was last viewed.

    The following rules are applied when creating the movie item:
    - If the movie's title contains a comma, the title is enclosed in double quotes.
    - If the movie has been viewed, the last viewed date is formatted as 'YYYY-MM-DD'. If the movie has not been viewed,
      the date is set to None.
    - If the movie has been rated by the user, the rating is rounded to the nearest whole number.
      If the movie has not been rated, the rating is set to None.

    Args:
        movie (Any): The movie object. For example:
            {
                "title": "The Shawshank Redemption",
                "year": 1994,
                "userRating": 9.3,
                "lastViewedAt": datetime.datetime(2021, 1, 1, 0, 0)
            }

    Returns:
        List[Any]: A list containing movie title, year, rating and date. For example:
            ["The Shawshank Redemption", 1994, "9", "2021-01-01"]
    """
    date: Optional[str] = None
    if movie.lastViewedAt is not None:
        date = movie.lastViewedAt.strftime('%Y-%m-%d')
    rating: Optional[str] = movie.userRating
    if rating is not None:
        rating = f'{movie.userRating:.0f}'
    title: str = movie.title
    if ',' in title:
        title = f'"{title}"'
    return [title, movie.year, rating, date]


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
            movie_details: List[List[Any]] = list(tqdm(executor.map(fetch_movie_details, found_movies), total=len(found_movies), desc="Fetching movie details"))
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
        all_movie_details: List[List[Any]] = fetch_section_details(sections)
        all_movie_details.insert(0, ['Title', 'Year', 'Rating10', 'WatchedDate'])
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
