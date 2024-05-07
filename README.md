1. Create a psql database and a corresponding user.

If needed, download and install postgreSQL. (On MacOS: `brew install postgresql`)

From the terminal, run,

`createdb cl`

`psql cl`

From within the PSQL shell that you just opened, run:

`CREATE ROLE cl WITH LOGIN PASSWORD 'cl' CREATEDB CREATEROLE;`

[dfarhi: I had to also run: `GRANT USAGE, CREATE ON SCHEMA public TO cl;`]

Do CTRL-D to leave the shell.

Then run `alembic upgrade head`` to run the alembic migrations. You'll need to pip install alembic if you don't already have it.

1.5 Install redis. If you are on windows this is a bit of a nightmare involving WSL, good luck. (Mac: `brew install redis`). Run it with `redis-server`

2. Local configs
* Make a file called local_settings.py in the root directory, and add `LOCAL = True` to it.
* Make a file called .env.local in the frontend/ directory, and add:
```
REACT_APP_URL=http://127.0.0.1:5002
REACT_APP_LOCAL='true'
```

3. Run the backend
* You'll want python 3.10 or later.
* Make a python venv if you want.
* `pip install -r requirements.txt`
* `python app.py`

4. Run the frontend
* If needed, install node.js. (`brew install node`)
* Go to the frontend/ directory,
* `npm install`
* `npm start`

You'll want to make a plots/ directory in the main directory of the repo if you want to test plotmaking/game stats stuff locally
