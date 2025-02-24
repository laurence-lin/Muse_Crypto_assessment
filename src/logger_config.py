import logging

FILE_PATH = '/mnt/d/laurence/big_data/stock_analysis/logs/extract_stock_log.log'


logger = logging.getLogger(__name__) # logger with name of this python file
if logger.hasHandlers():
    logger.handlers.clear()

print("reset new handlers!")
logging.basicConfig(level=logging.INFO
                        ,format='[%(asctime)s %(levelname)-8s] %(message)s'
	                    ,datefmt='%Y%m%d %H:%M:%S')
logger.addHandler(logging.FileHandler(FILE_PATH)) # Store log to file and show in shell