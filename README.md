**This repository is a fork of [Max Timkovich's plex2letterboxd](https://github.com/mtimkovich/plex2letterboxd.git) 
project.**

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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Authors

* [Arjun Earthperson][arjun_profile]
* [Max Timkovich][max_profile]

[import]: https://letterboxd.com/about/importing-data/
[max_profile]: https://letterboxd.com/djswerve/
[arjun_profile]: https://letterboxd.com/berryarjun/