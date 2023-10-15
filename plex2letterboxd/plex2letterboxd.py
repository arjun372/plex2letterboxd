"""Export watched Plex movies to the Letterboxd import format."""
import argparse
import configparser
import csv
import sys

from plexapi.myplex import MyPlexUser, MyPlexAccount
from plexapi.server import PlexServer
from typing import List, Any
import concurrent.futures


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
    Parse configuration file.

    Args:
        ini (str): Path to the configuration file.

    Returns:
        configparser.SectionProxy: SectionProxy object with configuration values.

    Raises:
        SystemExit: If any required configuration values are missing.
    """
    config: configparser.ConfigParser = configparser.ConfigParser()
    config.read(ini)
    auth: configparser.SectionProxy = config['auth']
    missing: set = {'baseurl', 'token'} - set(auth.keys())
    if missing:
        print(f'Missing the following config values: {missing}')
        sys.exit(1)
    return auth


def fetch_movie_details(movie):
    """
    Fetch details of a movie.

    Args:
        movie: Movie object.

    Returns:
        list: List containing movie title, year, rating and date.
    """
    date: str = None
    if movie.lastViewedAt is not None:
        date = movie.lastViewedAt.strftime('%Y-%m-%d')
    rating: str = movie.userRating
    if rating is not None:
        rating = f'{movie.userRating:.0f}'
    print(movie.title, movie.year, rating, date)
    return [movie.title, movie.year, rating, date]


def fetch_section_details(sections, max_workers=None):
    """
       Fetch details of all movies in the given sections.

       Args:
           sections (list): List of section objects.
           max_workers (int, optional): Maximum number of threads that can be used to execute the given calls.

       Returns:
           list: List of lists containing details of all movies.
    """
    all_movie_details = []
    for section in sections:
        found_movies = section.search(sort='lastViewedAt', unwatched=False)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            movie_details = list(executor.map(fetch_movie_details, found_movies))
            all_movie_details.extend(movie_details)
    return all_movie_details


def write_csv(sections: List[Any], output: str) -> None:
    """
    Write movie details to a CSV file.

    Args:
        sections (List[Any]): List of section objects.
        output (str): Path to the output file.
    """
    with open(output, 'w', newline='') as f:
        writer = csv.writer(f)
        all_movie_details = [['Title', 'Year', 'Rating10', 'WatchedDate']]
        all_movie_details.extend(fetch_section_details(sections))
        writer.writerows(all_movie_details)


def main() -> None:
    """
    Main function to parse arguments, parse configuration, fetch movie details and write them to a CSV file.
    """
    args: argparse.Namespace = parse_args()
    auth: configparser.SectionProxy = parse_config(args.ini)

    plex: PlexServer = PlexServer(auth['baseurl'], auth['token'])
    if args.managed_user:
        myplex: MyPlexAccount = plex.myPlexAccount()
        user: MyPlexUser = myplex.user(args.managed_user)
        token: str = user.get_token(plex.machineIdentifier)
        plex = PlexServer(auth['baseurl'], token)

    sections: List[Any] = [plex.library.section(s) for s in args.sections]
    write_csv(sections, args.output)
    