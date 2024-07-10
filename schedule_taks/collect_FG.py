import schedule
import time
import datetime
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy import insert, select
import requests

# Database setup
engine = create_engine("postgresql+psycopg2://postgres:mierda69@localhost:5432/Crypto_Collection")
metadata = MetaData()

# Define your table structure
user_table = Table('fear_greed', metadata,
                   Column('id', Integer, primary_key=True),
                   Column('datetime_price', String),
                   Column('fear_greed', String))

metadata.create_all(engine)

# Function to fetch Fear and Greed Index
def get_today_FAG():
    url = "https://api.alternative.me/fng/?limit=2"
    response = requests.get(url).json()
    return response['data'][0]['value']

# Function to push data to the database
def push_data(fear_greed: str):
    with engine.connect() as conn:
        stmt = (
            insert(user_table).
            values(datetime_price=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), fear_greed=fear_greed)
        )
        conn.execute(stmt)
        conn.commit()  # Ensure the transaction is committed
        print("Data pushed:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), fear_greed)  # Logging

# Function to determine yesterday's message
def determine_message():
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    with engine.connect() as conn:
        stmt = select(user_table).where(user_table.c.datetime_price.like(f'{yesterday}%'))
        result = conn.execute(stmt).fetchone()
        if result:
            return result['fear_greed']
        else:
            return "No data for yesterday"

if __name__ == "__main__":
    fear_greed_value = get_today_FAG()
    push_data(fear_greed_value)
    print(determine_message())
