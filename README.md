# To run:
1. Populate required data for creating postgres tables and prediction bases by adding required `json` into `scripts/db`
2. Create SQL file by running `scripts/generate_sql.py` (outputs SQL to stdout, pipe it to file using `python3 generate_sql.py > setup.sql`)
3. Move SQL file to `db_setup`. Filenames in this folder can be anything, .sql files will be ran in on init (when postgres db hasn't been initialised)
4. Ensure that new pcap files are being added to any folder in `wild_data`. For example `wild_data/folder_1/capture_1.pcap` will be read but `wild_data/capture_1.pcap` will not. Also ensure that paths to each pcap are unique (`folder_1/capture_1.pcap`, `folder_2/capture_1.pcap` will both be read). pcap files placed in this folder will be deleted after reading. If path is reused it will not be read (if `folder_1/capture_1.pcap` is read and deleted, adding a file by the same name in the same folder will not be read.)
5. Compose containers using `sudo docker compose up --build -d`
6. Visit https://127.0.0.1:3000 and login with login: admin, password: admin

`reset_data.sh`
Deletes all data from database
After resetting db, the `data` docker container likely failed to start. run `sudo docker start data`

`scripts/generate_sql.py`
Python script for generating `init.sql`. Reads command line arguments for json files containing devices as highest level keys, and features as second level keys.
Creates tables, populates device map with unique ids, outputs to `stdout`. Ideally piped into a file.

**Be sure to replace `db_setup/setup.sql` with new SQL file and delete old database otherwise changes may not apply**

See `scripts/generate_data.py/predict_signatures` for data prediction and upload to db.
