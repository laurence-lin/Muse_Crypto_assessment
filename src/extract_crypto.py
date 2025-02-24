import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from datetime import datetime ,timedelta
import logging
from airflow.exceptions import AirflowSkipException
from airflow.operators.python import get_current_context
from airflow.decorators import task
from psycopg2 import sql
from psycopg2.extensions import register_adapter, AsIs
from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    DateTime,
    Numeric
)
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

# Setup logging
FILE_PATH = '/mnt/c/Users/User/laurence/Muse_assessment/logs/extract_stock_log.log'


logger = logging.getLogger(__name__) # logger with name of this python file

print("reset new handlers!")
logging.basicConfig(level=logging.INFO
                        ,format='[%(asctime)s %(levelname)-8s] %(message)s'
	                    ,datefmt='%Y%m%d %H:%M:%S')
logger.addHandler(logging.FileHandler(FILE_PATH)) # Store log to file and show in shell



# 1. Connect to DWH database
# connect URL: dialect+driver://username:password@host:port/database
#local_url = 'postgresql+psycopg2://postgres:postgres@localhost:5432/postgres'
#engine = create_engine(local_url, echo=True)


supabase_url = 'postgresql://postgres.iczymixwwbkvexasaalk:[YOUR-PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres'


# Load environment variables from .env
load_dotenv()

# Fetch variables
USER = os.getenv("SUPABASE_USER")
PASSWORD = os.getenv("SUPABASE_DB_PWD")
HOST = os.getenv("SUPABASE_HOST")
PORT = 5432  #os.getenv("port")
DBNAME = "postgres"  #os.getenv("dbname")

# Construct the SQLAlchemy connection string
DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)
# If using Transaction Pooler or Session Pooler, we want to ensure we disable SQLAlchemy client side pooling -
# https://docs.sqlalchemy.org/en/20/core/pooling.html#switching-pool-implementations
# engine = create_engine(DATABASE_URL, poolclass=NullPool)

# Test the connection
try:
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print(f"Failed to connect: {e}")

# Postgres Table Schema definition
register_adapter(pd._libs.missing.NAType, lambda i: AsIs('NULL')) # register pd.NA type as postgres NULL

Base = declarative_base()

class crypto_price(Base):
    # Schema for bitcoin price
    __tablename__ = 'muse_project'
    id = Column(Integer, primary_key=True, autoincrement=True)
    update_time = Column(DateTime(timezone=True))
    crypto_name = Column(String)
    price = Column(Numeric)
    hour_change_rate = Column(Numeric)
    volume = Column(Numeric)


def scrape_coinmarketcap_top10(url = "https://coinmarketcap.com/"):
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses

        soup = BeautifulSoup(response.content, "html.parser")
        #sc-936354b2-3 tLXcG cmc-table
        table = soup.find("tbody") #Updated Class Name
        if not table:
            print("Table not found.")
            return None

        rows = table.find_all("tr")[:10]  # Updated Class Name, and limit to top 10 rows.

        crypto_data = []
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 7:  # Ensure enough cells are present
                name_cell = cells[2].find('p') #Updated class name.
                name = name_cell.text.strip() if name_cell else "N/A"
                price_cell = cells[3].find('span')
                price = price_cell.text.strip() if price_cell else "N/A"
                change_1h_cell = cells[4].find('span')
                change_1h = change_1h_cell.text.strip() if change_1h_cell else "N/A"
                if change_1h_cell:
                    change_attr = change_1h_cell.find_all('span', class_=['icon-Caret-down', 'icon-Caret-up']) # Get up or down: icon-Caret-up -> +, icon-Caret-down -> -
                    if change_1h:
                        if 'icon-Caret-down' in str(change_attr[0]):
                            change_1h = "-" + change_1h
                
                volume_cell = cells[8].find('p', {'color':'text'}) #Updated class name
                volume = volume_cell.text.strip() if volume_cell else "N/A"

                # Preprocess
                price = float(price.split('$')[1].replace(',', ''))
                change_1h = float(change_1h.replace('%', ''))
                volume = float(volume.replace(',', '').replace('$',''))
                crypto_data.append({
                    "crypto_name": name,
                    "price": price,
                    "hour_change_rate": change_1h,
                    "volume": volume,
                    "update_time": datetime.now()
                })

        print("Done data extraction. Start storing to DB...")
        logger.info("Done data extraction. Start storing to DB...")
        with Session(engine) as sess:
            sess.bulk_insert_mappings(crypto_price, 
                                    crypto_data)
            sess.commit()

        print("Done bulk insert.")

        return crypto_data

    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None




if __name__ == '__main__':

    
    try:
        
        print("Start extracting bitcoin real-time price...")
        logger.info(f"{datetime.now()} Start extracting bitcoin real-time price...")
        #extract_stock(stock_meta)
        scrape_coinmarketcap_top10()
        print("Done price extraction.")
        logger.info(f"{datetime.now()} Done price extraction.")
        
    except Exception as e:
        print("Price extraction failed in the middle, exception: ", e)
        logger.info("Price extraction failed in the middle, exception: ", e)
