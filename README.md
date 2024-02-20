Create a psql database and a corresponding user. From the terminal, run,

`createdb cl`

`psql cl`

From within the PSQL shell that you just opened, run:

`CREATE ROLE cl WITH LOGIN PASSWORD 'cl' CREATEDB CREATEROLE;`

Do CTRL-D to leave the shell.

Then run alembic upgrade head to run the alembic migrations. You'll need to pip install alembic if you don't already have it.

To run the backend, do python app.py. You'll want python 3.9 or later. You can pip install the relevant packages; the only tricky one I can remember off the top of my head is the redis lock package, which is python-redis-lock. 

To run the frontend, go to the frontend/ directory, do npm install, and then npm start.

