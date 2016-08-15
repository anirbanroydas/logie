
"""This module defines the base loggers that can be used to log any kinds of data be it, debug, info, error, warning, critical,
both in a log file and also in the I/O stream.

To change the name of log file, or log level for file and also for stream, just change the constants at the top level.

This is configurable as per your requirements.
"""

# Initate logging loggers, and handlers
import logging
import os

print '[log.py] Entered Module'

print '[log.py] calling relative import logie.settings.py'
from logie.settings import DEFAULT_APPINFO_APPNAME, DEFAULT_STORAGE_PATH, DEFAULT_APPLOG_PATH, DEFAULT_APPLOG_APPEND, DEFAULT_STORAGE_APPEND, CONFIG_DATA
print '[log.py] returned from relative import logie.settings.py'

# create formatter
DEFAULT_FORMAT = '[%(loglevel)s]: [%(logtime)s] [App - %(app_name)s] [Module - %(module)s] [Function - %(function)s:%(linenum)d] - %(logmsg)s'
DEFAULT_DATE_FORMAT = '%d-%m-%y %H:%M:%S'
DEFAULT_LOG_FILE = DEFAULT_STORAGE_PATH + '/' + \
    DEFAULT_APPINFO_APPNAME + '/' + DEFAULT_APPINFO_APPNAME + '.log'
DEFAULT_FILE_LOGLEVEL = logging.INFO
DEFAULT_STREAM_LOGLEVEL = logging.ERROR
DEFAULT_LOGGER_LOGLEVEL = logging.INFO
DEFAULT_FILE_APPEND = DEFAULT_STORAGE_APPEND

# max bytes for rotating file
MAX_BYTES = 50428800

# No. of rotating files
BACKUP_COUNT = 5

# create default value for logie's logging
APP_DEFAULT_FORMAT = '[%(levelname)s]: [%(asctime)s]  [%(name)s] [%(module)s:%(lineno)d] - %(message)s'
APP_DEFAULT_DATE_FORMAT = '%d-%m-%y %H:%M:%S'
APP_DEFAULT_LOG_FILE = DEFAULT_APPLOG_PATH
APP_DEFAULT_FILE_LOGLEVEL = logging.DEBUG
APP_DEFAULT_STREAM_LOGLEVEL = logging.DEBUG
APP_DEFAULT_LOGGER_LOGLEVEL = logging.DEBUG
APP_DEFAULT_FILE_APPEND = DEFAULT_APPLOG_APPEND



# create console handler and set level to DEBUG
stream_handler = logging.StreamHandler()
stream_handler.setLevel(APP_DEFAULT_STREAM_LOGLEVEL)

formatter = logging.Formatter(APP_DEFAULT_FORMAT, APP_DEFAULT_DATE_FORMAT)

# add formatter to handler
stream_handler.setFormatter(formatter)

# initiate a logger
LOGGER = logging.getLogger(__name__)

# set level for Logger
LOGGER.setLevel(APP_DEFAULT_LOGGER_LOGLEVEL)

# add handler to logger
LOGGER.addHandler(stream_handler)



# LOGGER = get_null_logger_logie(__name__)






def initiate_loggers():
	LOGGER.debug('inside initiate_loggers')
	
	global DEFAULT_LOG_FILE
	global DEFAULT_FILE_APPEND
	global APP_DEFAULT_LOG_FILE
	global APP_DEFAULT_FILE_APPEND
	appinfo_app_name = None
	storage_path = None
	storage_append = None
	applog_path = None
	applog_append = None

	if CONFIG_DATA:
		appinfo_app_name = CONFIG_DATA['appinfo']['app_name'] if 'appinfo' in CONFIG_DATA and 'app_name' in CONFIG_DATA['appinfo'] else DEFAULT_APPINFO_APPNAME
		storage_path = CONFIG_DATA['storage']['path'] if 'storage' in CONFIG_DATA and 'path' in CONFIG_DATA['storage'] else DEFAULT_STORAGE_PATH
		# self.storage_type = config_data['storage']['type'] if 'storage' in
		# config_data and 'type' in config_data['storage'] else
		# DEFAULT_STORAGE_TYPE
		storage_append = CONFIG_DATA['storage']['file_append'] if 'storage' in CONFIG_DATA and 'file_append' in CONFIG_DATA['storage'] else DEFAULT_STORAGE_APPEND
		applog_path = CONFIG_DATA['applog']['path'] if 'applog' in CONFIG_DATA and 'path' in CONFIG_DATA['applog'] else DEFAULT_APPLOG_PATH
		# self.applog_type = config_data['applog']['type'] if 'applog' in
		# config_data and 'type' in config_data['applog'] else DEFAULT_APPLOG_TYPE
		applog_append = CONFIG_DATA['applog']['file_append'] if 'applog' in CONFIG_DATA and 'file_append' in CONFIG_DATA['applog'] else DEFAULT_APPLOG_APPEND
		# self.separate = config_data['loginfo']['separate'] if 'loginfo' in
		# config_data and 'separate' in config_data['loginfo'] else
		# DEFAULT_FILE_SEPARATION 


	else:
		appinfo_app_name = DEFAULT_APPINFO_APPNAME
		storage_path = DEFAULT_STORAGE_PATH
		# self.storage_type = DEFAULT_STORAGE_TYPE
		storage_append = DEFAULT_FILE_APPEND
		applog_path = APP_DEFAULT_LOG_FILE
		# self.applog_type = DEFAULT_APPLOG_TYPE
		applog_append = DEFAULT_APPLOG_APPEND
		# self.separate = DEFAULT_FILE_SEPARATION


	DEFAULT_LOG_FILE = storage_path + '/' + appinfo_app_name + '/' + appinfo_app_name + '.log'
	DEFAULT_FILE_APPEND = storage_append
	APP_DEFAULT_LOG_FILE = applog_path
	APP_DEFAULT_FILE_APPEND = applog_append





def get_file_logger():
	"""Function to return the logger for each module used in the application. 

		:param 	module_name: 	the module name where the logger is called from 
		:type 	moduele_name: 	str
		:rerturn: 				The logger object 
		:rtype: 				logging.LOGGER 
	
	"""

	LOGGER.debug('inside get_file_logger')
	# File logging
	# logging.basicConfig(level=DEFAULT_FILE_LOGLEVEL, filename=DEFAULT_LOG_FILE, format=DEFAULT_FORMAT, datefmt=DEFAULT_DATE_FORMAT)

	# create file if not there
	if not os.path.exists(os.path.dirname(os.path.abspath(DEFAULT_LOG_FILE))):
	    try:
	        os.makedirs(os.path.dirname(os.path.abspath(DEFAULT_LOG_FILE)))
	    except OSError:  # Guard against race condition
	        # if exc.errno != errno.EEXIST:
	        raise
		with open(DEFAULT_LOG_FILE, 'wb') as f:
		    f.write('')

	LOGGER.debug('File Handler : File : %s ' % DEFAULT_LOG_FILE)




	# rotating file handler
	file_handler = logging.handlers.RotatingFileHandler(
	    filename=DEFAULT_LOG_FILE, mode=DEFAULT_FILE_APPEND, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding=None, delay=0)
	file_handler.setLevel(DEFAULT_FILE_LOGLEVEL)

	# create formatter
	formatter = logging.Formatter(DEFAULT_FORMAT, DEFAULT_DATE_FORMAT)

	# add formatter to handler
	file_handler.setFormatter(formatter)

	# initiate a logger
	logger = logging.getLogger(DEFAULT_APPINFO_APPNAME)

	# set level for Logger
	logger.setLevel(DEFAULT_LOGGER_LOGLEVEL)

	# add handler to logger
	logger.addHandler(file_handler)

	return logger



def get_stream_logger():
	LOGGER.debug('inside get_stream_logger')
	# create console handler and set level to DEBUG
	stream_handler = logging.StreamHandler()
	stream_handler.setLevel(DEFAULT_STREAM_LOGLEVEL)

	# create formatter
	formatter = logging.Formatter(DEFAULT_FORMAT, DEFAULT_DATE_FORMAT)

	# add formatter to handler
	stream_handler.setFormatter(formatter)

	# initiate a logger
	logger = logging.getLogger(DEFAULT_APPINFO_APPNAME)

	# set level for Logger
	logger.setLevel(DEFAULT_LOGGER_LOGLEVEL)

	# add handler to logger
	logger.addHandler(stream_handler)

	return logger




def set_adapter(logger, extra):

	# add logging adapter to adapt to new format
	new_logger = logging.LoggerAdapter(logger, extra)

	return new_logger




def get_logger_logie(module_name):
	"""Function to return the logger for each module used in the application. 

		:param 	module_name: 	the module name where the logger is called from 
		:type 	moduele_name: 	str
		:rerturn: 				The logger object 
		:rtype: 				logging.LOGGER 
	
	"""
	LOGGER.debug('inside get_logger_logie')

	# File logging
	# logging.basicConfig(level=DEFAULT_FILE_LOGLEVEL, filename=DEFAULT_LOG_FILE, format=DEFAULT_FORMAT, datefmt=DEFAULT_DATE_FORMAT)
	
	# create file if not there
	# print APP_DEFAULT_LOG_FILE
	# print os.path.exists(APP_DEFAULT_LOG_FILE)
	# print os.path.dirname(os.path.abspath(APP_DEFAULT_LOG_FILE))
	if not os.path.exists(os.path.dirname(os.path.abspath(APP_DEFAULT_LOG_FILE))):
	    try:
	        os.makedirs(os.path.dirname(os.path.abspath(APP_DEFAULT_LOG_FILE)))
	    except OSError:  # Guard against race condition
	        # if exc.errno != errno.EEXIST:
	        raise
		with open(APP_DEFAULT_LOG_FILE, 'wb') as f:
		    f.write('')

	LOGGER.debug('File Handler : File : %s ' % APP_DEFAULT_LOG_FILE)



	# rotating file handler
	file_handler = logging.handlers.RotatingFileHandler(
	    filename=APP_DEFAULT_LOG_FILE, mode=APP_DEFAULT_FILE_APPEND, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding=None, delay=0)
	file_handler.setLevel(APP_DEFAULT_FILE_LOGLEVEL)

	# create console handler and set level to DEBUG
	stream_handler = logging.StreamHandler()
	stream_handler.setLevel(APP_DEFAULT_STREAM_LOGLEVEL)

	formatter = logging.Formatter(APP_DEFAULT_FORMAT, APP_DEFAULT_DATE_FORMAT)

	# add formatter to handler
	stream_handler.setFormatter(formatter)
	file_handler.setFormatter(formatter)

	# initiate a logger
	logger = logging.getLogger(module_name)

	# set level for Logger
	logger.setLevel(APP_DEFAULT_LOGGER_LOGLEVEL)

	# add handler to logger
	logger.addHandler(stream_handler)
	logger.addHandler(file_handler)

	return logger


def get_null_logger_logie(module_name): 
	print '[logie.logger.log.py] inside get_null_logger_logger'
	# create console handler and set level to DEBUG
	null_handler = logging.NullHandler()
	# null_handler.setLevel(DEFAULT_STREAM_LOGLEVEL)

	# # create formatter
	# formatter = logging.Formatter(DEFAULT_FORMAT, DEFAULT_DATE_FORMAT)

	# # add formatter to handler
	# null_handler.setFormatter(formatter)

	# initiate a logger
	logger = logging.getLogger(module_name)

	# set level for Logger
	logger.setLevel(DEFAULT_LOGGER_LOGLEVEL)

	# add handler to logger
	logger.addHandler(null_handler)

	return logger







