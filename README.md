# Plex2Letterboxd

Plex2Letterboxd is a Python script that exports watched movies from Plex to the [Letterboxd Import Format][import]. 
The exported data includes the movie title, release year, user rating, and the last watched date. 
This data is exported to a CSV file which can be easily imported into Letterboxd. However, until Letterboxd makes their
API public, this CSV will need to be uploaded manually.

## Features

- Export watched movies from Plex to CSV in Letterboxd import format.
- Multi-threaded fetching of movie details for faster execution.
- Supports managed users in Plex.
- Configurable sections to grab movies from.

## Prerequisites

- Python 3.6 or higher
- Access to a Plex server

## Installation

Clone the repository and install the dependencies:

```console
$ git clone https://github.com/arjun372/plex2letterboxd.git
$ cd plex2letterbox
$ pip install .
```

## Configuration

Rename `config.ini.example` to `config.ini` and fill it with your Plex server details:

```ini
[auth]
baseurl = http://localhost:32400
token = YourPlexToken
```

- `baseurl`: The URL of your Plex server.
- `token`: Your Plex access token. You can find this by following [these instructions](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/).

## Usage

Run the script with the configuration file:

```console
$ python -m plex2letterboxd -i config.ini
```

### Command Line Arguments

```
optional arguments:
  -h, --help            show this help message and exit
  -i INI, --ini INI     config file (default: config.ini)
  -o OUTPUT, --output OUTPUT
                        file to output to (default: letterboxd.csv)
  -s [SECTIONS [SECTIONS ...]], --sections [SECTIONS [SECTIONS ...]]
                        sections to grab from (default: ['Movies'])
  -m, --managed-user    name of managed user to export
```

The generated CSV file can be uploaded to Letterboxd at https://letterboxd.com/import/.

## Output

The script generates a CSV file in the following format:

| Title         | Year           | Rating10      | WatchedDate         |
|---------------|----------------|---------------|---------------------|
| Movie Title 1 | Release Year 1 | User Rating 1 | Last Watched Date 1 |
| Movie Title 2 | Release Year 2 | User Rating 2 | Last Watched Date 2 |
| ...           | ...            | ...           | ...                 |

Here is an example of what the output might look like. Note that the rating is optional.

```shell
$ cat letterboxd.csv
Title,Year,Rating10,WatchedDate
Llamageddon,2015,,2023-10-12
The General,1926,8,2022-01-01
His Girl Friday,1940,,2021-11-02
The Kid,1921,,2021-07-03
```

## Import into Letterboxd

1. Go to https://letterboxd.com/import/.
2. Click on 'Choose file' and select the generated CSV file.
3. Click on 'Import'.

## Development

### Testing

The script comes with a set of unit tests that can be run to verify its functionality. 
To run the tests, navigate to the root directory of the project and execute the following command:

```shell
python -m unittest discover tests
```
This command will discover and run all the test cases that are present in the `tests` directory. Please ensure that you
have all the necessary permissions and configurations set up correctly before running the tests. If you encounter any 
issues while running the tests, feel free to open an issue.

### Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your changes.
3. Make your changes in your branch.
4. Submit a pull request.

### Authors

* [Arjun Earthperson][arjun_profile]
* [Max Timkovich][max_profile]

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

### Contact

For any questions or support, please contact the maintainers:

- Arjun Earthperson: [mail@earthperson.org](mailto:mail@earthperson.org)
- Max Timkovich: [max@timkovi.ch](mailto:max@max@timkovi.ch)

[import]: https://letterboxd.com/about/importing-data/
[max_profile]: https://letterboxd.com/djswerve/
[arjun_profile]: https://letterboxd.com/berryarjun/