# Book publishing platform hacked up as fast as possible

## Tech

* Flask
* Postgres

## Install

1. Install [homebrew](http://brew.sh/)
1. Upgrade XCode to the latest Version (via Mac Appstore)
1. Install python3 and pip3 with  `brew install python3`
1. Install virtualenv with `sudo pip3 install virtualenv`
1. Install Postgres using [Postgress.app](http://postgresapp.com/)
1. Clone this project to your machine
1. Activate the virtualenv
1. Install dependencies from requirements.txt
1. Run
1. Navigate to localhost:3003

## Postgres Setup

* Add Postgres to your path by adding the following line to `~/.profile`

```export PATH=$PATH:/Applications/Postgres.app/Contents/Versions/latest/bin```

1. Run `psql` in terminal
1. Run `createdb db_name`
1. List your databases with `\list` to make sure db_name was created
1. 


## Software Versions in Development

| Tool       | Version  |
|------------|----------|
| Homebrew   | 1.1.1    |
| Postgres   | 9.6.1.0  |
| XCode      | 8.1      |
| Python3    | 3.5.2    |
| pip3       | 8.1.2    |
| virtualenv | 15.1.0   |

## Misc. Info

* Uses Skeleton 2.0.4 for styling: `https://github.com/dhg/Skeleton/tree/gh-pages`

## Development Commands

* Activate virtualenv: `source env/bin/activate`
* Deactivate virtualenv: `deactivate`
* Start server: `env/bin/python run.py`

## Project Setup Commands

* Create virtualenv: `virtualenv env`
* Install package: `pip3 install package_name`
* Save installed packages to file: `pip freeze > requirements.txt`
* Install packages from file: `pip install -r requirements.txt`


