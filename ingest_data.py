import os
import argparse
import pandas as pd
from sqlalchemy import create_engine
from time import time

def main(params):
    user = params.user
    password = params.password 
    host = params.host 
    port = params.port 
    db = params.db 
    table_name1 = params.table_name1 
    url1 = params.url1
    csv_name1 = url1.split("/")[-1]

    table_name2 = params.table_name2
    url2 = params.url2
    csv_name2 = url2.split("/")[-1]

    os.system(f"wget {url1} -O {csv_name1}")
    os.system(f"wget {url2} -O {csv_name2}")

    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    df_zones = pd.read_csv(csv_name2)
    df_iter = pd.read_csv(csv_name1,iterator=True,chunksize=100000)

    df = next(df_iter)

    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)


    df.head(n=0).to_sql(name=table_name1,con=engine,if_exists='replace')
    df_zones.to_sql(name=table_name2,con=engine,if_exists='replace')

    df.to_sql(name=table_name1, con=engine, if_exists='append')
    
    while True:
        t_start = time()
        df=next(df_iter)
        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
        df.to_sql(name=table_name1,con=engine,if_exists='append')
        t_end = time()
        print('chonked... took %.3f second' % (t_end - t_start))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest data to Postgres')
    parser.add_argument('--user',help='user for postgres')
    parser.add_argument('--password',help='password for postgres')
    parser.add_argument('--host',help='host for postgres')
    parser.add_argument('--port',help='port for postgres')
    parser.add_argument('--db',help='database for postgres')
    parser.add_argument('--table_name1',help='table name for postgres')
    parser.add_argument('--url1',help='csv file url')
    parser.add_argument('--table_name2',help='table name for postgres')
    parser.add_argument('--url2',help='csv file url')
    args = parser.parse_args()

    main(args)