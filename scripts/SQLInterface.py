import psycopg2
import pandas as pd
import os

class SQLInterface:
    def connect(self):
        credentials = {
            "host":os.environ["host"],
            "user": os.environ["user"],
            "password": os.environ["passwd"],
            "port": os.environ["port"],
            'dbname' : os.environ['db']
        }
        
        self.connection = psycopg2.connect(**credentials)

        self.cursor = self.connection.cursor()

    def check_connect(self):
        if 'connection' not in self.__dict__ or self.connection.closed != 0:
            self.connect()
        try:
            self.connection.isolation_level
        except psycopg2.OperationalError as oe:
            self.connect()

    def execute(self, sql, args = []) -> None:
        self.check_connect()

        with self.connection.cursor() as cursor:
            cursor.execute(sql, args)
        self.commit()

    
    def execute_pd(self, sql, args = []) -> pd.DataFrame:
        self.check_connect()

        df = pd.read_sql(sql, self.connection, params = list(args))

        return df
    
    def commit(self):
        self.connection.commit()
    
    def close(self):
        self.connection.close()

    def insert_pd(self, df:pd.DataFrame, name):
        self.check_connect()
        d = df.to_dict('split')
        self.insert_dict(name, d['columns'], d['data'])
        # df.to_sql(name, con = self.connection, if_exists=if_exists, **kwargs)
    
    def insert_dict(self, name, columns:list, data:list):
        """
            `name`: name of table
            same contents as result of pd.Dataframe.to_dict('split')
            `columns` contains list of strings of column names (in order of values in `data`)
            `data` contains lists of values (corresponding to a row)
            eg.[
                ['Device 1', '1970-01-01T00:00:01.710125244'],
                ['Device 1', '1970-01-01T01:00:01.710125244'],
            ]
        """
        self.check_connect()
        base_query = f"insert into {name}({','.join(columns)}) values ({','.join(['%s']*len(columns))});"

        def process_value(value):
            """
                Ensure value can be accepted by postgres
            """
            if isinstance(value, pd.Timestamp):
                return value.isoformat()
            return value

        for row in data:
            self.execute(base_query, [process_value(v) for v in row])
