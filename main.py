import time
import logging
import psutil
import json
import os
import uuid
import numpy as np
import pandas as pd
import pathlib
import argparse
from datetime import datetime, timedelta
from concurrent_log_handler import ConcurrentRotatingFileHandler

from src.scrapper import TokpedScrapper

#setup logging to file
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d %B %Y %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        ConcurrentRotatingFileHandler(
            filename='./logs/TokpedScrapper.log',
            mode='a',
            maxBytes=20 * 1024 * 1024,
            backupCount=3
        )
    ],
)

parser = argparse.ArgumentParser(description='Tokopedia Scrapper')
parser.add_argument("--scrape_url", "-su", type=str, default = '', help="Official account url from Tokopedia")

args = parser.parse_args()

def main():
    logger = logging.getLogger("Main")
    logger.info('*'*45 + ' START ' + '*'*45)

    start_main = datetime.now()
    exit_status = 0

    try:
        # Get URL scrapper
        scrape_url = args.scrape_url

        # Define data ID
        data_id = '071541c3-eb7a-4a73-9f85-11d49f683eea'

        # Create new folder
        os.makedirs(f'data/{data_id}/', exist_ok = True)

        # Create new FireFox session
        scrapper = TokpedScrapper(
            data_id = data_id
        )
        scrapper.create_firefox_session()

        # Get the scrape url
        video_post_links = scrapper.get_post_link(scrape_url)

        # Create empty dataframe for storing data_metadata and qna_aetadata
        data_metadata_df = pd.DataFrame()
        qna_metadata_df = pd.DataFrame()

        # Loop 
        for link in video_post_links[40:]:
            try:
                # Get data metadata
                data_metadata = pd.DataFrame([scrapper.get_data_metadata(link)])
                data_metadata_df = pd.concat([data_metadata_df, data_metadata], axis=0, ignore_index=True)

                # Get qna metadata
                qna_metadata = pd.DataFrame(scrapper.get_qna_metadata(max_qna_page = 3))
                qna_metadata_df = pd.concat([qna_metadata_df, qna_metadata], axis=0, ignore_index=True)
            
            except Exception as e:
                logger.error(e)
                continue

        # Quit session
        scrapper.quit_session()

        # Save data_metadata and qna_metadata
        if os.path.exists(f'data/{data_id}/data_metadata.csv'):
            past_data_metadata_df = pd.read_csv(f'data/{data_id}/data_metadata.csv')
            updated_data_metadata_df = pd.concat([past_data_metadata_df, data_metadata_df], axis = 0, ignore_index=True)
            updated_data_metadata_df.to_csv(f'data/{data_id}/data_metadata.csv', index = False)
        else:
            data_metadata_df.to_csv(f'data/{data_id}/data_metadata.csv', index = False)
        
        if os.path.exists(f'data/{data_id}/qna_metadata.csv'):
            past_qna_metadata_df = pd.read_csv(f'data/{data_id}/qna_metadata.csv')
            updated_qna_metadata_df = pd.concat([past_qna_metadata_df, qna_metadata_df], axis = 0, ignore_index=True)
            updated_qna_metadata_df.to_csv(f'data/{data_id}/qna_metadata.csv', index = False)
        else:
            qna_metadata_df.to_csv(f'data/{data_id}/qna_metadata.csv', index = False)

    except BaseException as e:
        exit_status = 1
        logger.exception(e)
        raise e

    finally:
        end_main = datetime.now()
        logger.info(f'Exited after {end_main - start_main} with status {exit_status}')
        logger.info('*'*45 + ' FINISH ' + '*'*45)

if __name__ == '__main__':
    main()