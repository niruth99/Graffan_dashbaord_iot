# To run:
sudo docker compose up --build -d
visit https://127.0.0.1:3000 and login with login: admin, password: admin

`reset_data.sh`
Deletes all data from database

`scripts/generate_sql.py`
Python script for generating `init.sql`. Reads command line arguments for json files containing devices as highest level keys, and features as second level keys.
Creates tables, populates device map with unique ids, outputs to `stdout`. Ideally piped into a file.

**Be sure to replace `db_setup/setup.sql` with new SQL file and delete old database otherwise changes may not apply**

See `scripts/generate_data.py/predict_signatures` for data prediction and upload to db.
