import logging
import argparse
import os
import pandas as pd

from covid_utils import logs
from covid_utils import connect
from covid_utils import credentials
from covid_utils import local_config

from d3 import queries

class FlatFileGenerator(object):
    def __init__(self, env='local'):
        logs.configure_logging('FFGenerator')
        self.logger = logging.getLogger()

        self.env = env
        self.data_file_root = os.path.expanduser(local_config.data_repo_path)

        self.sql_dict = queries.sql_dict

        self.connect_to_postgres()

    def connect_to_postgres(self):
        self.logger.info("Connecting to postgres..")
        self.pg_creds = credentials.get_postgres_creds(self.env)
        self.conn = connect.pandas_dbconn(self.pg_creds, self.env)
        self.logger.info("Connected to postgres at {}.".format(self.pg_creds['host']))

    def fetch_data(self, sql):
        self.sql_key = sql
        self.logger.info(f"Running {self.sql_key} query...")
        self.sql_to_run = queries.sql_dict[self.sql_key]

        self.logger.info(f"Using this sql: {self.sql_to_run}")
        self.df = pd.read_sql(self.sql_to_run, self.conn)
        self.df = self.df.fillna(0)

    def write_csv(self):
        self.logger.info("Forming filename.")
        self.full_output_path = f"{self.data_file_root}/{self.sql_key}.csv"

        self.logger.info(f"Writing to {self.full_output_path}")
        self.df.to_csv(self.full_output_path, index=False)

        self.logger.info("Done writing file.")


if __name__ == "__main__":

    arguments = argparse.ArgumentParser()
    arguments.add_argument('-s', '--sql', help='sql to use from dict')
    arguments.add_argument('-e', '--env', help='environment this script is running in', default='local')
    args = arguments.parse_args()

    sql = args.sql
    output = f"{args.sql}.csv"
    if sql is None:
        sql = 'daily_by_state'
        output = 'daily_by_state.csv'

    ff = FlatFileGenerator(env)
    ff.fetch_data(sql)
    ff.write_csv()
