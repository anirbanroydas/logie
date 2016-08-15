# # Initate logging loggers, and handlers
# import logging


# # create console handler and set level to info
# handler = logging.StreamHandler()
# handler.setLevel(logging.INFO)


# # create formatter
# DEFAULT_FORMAT = '[%(levelname)s]: [%(asctime)s]  [%(name)s] [%(module)s:%(lineno)d] - %(message)s'
# DEFAULT_DATE_FORMAT = '%d-%m-%y %H:%M:%S'
# formatter = logging.Formatter(DEFAULT_FORMAT, DEFAULT_DATE_FORMAT)

# # add formatter to handler
# handler.setFormatter(formatter)

# # initiate a logger
# logger = logging.getLogger(__name__)

# # set level for Logger
# logger.setLevel(logging.INFO)

# # add handler to logger
# logger.addHandler(handler)

print '[__init__.py] Entered MAIN logie Module'

print '[__init__.py] calling relative import logie.settings'
from .settings import DEFAULT_EXCHANGE, EXCHANGE_TYPE
print '[__init__.py] returned from relative import logie.settings'


print '[__init__.py] calling relative import logie.apps.logger.client'
from logie.apps.logger.client import Logger 
print '[__init__.py] returned from relative import logie.apps.logger.client'


def get_logie(app_name='default', stdio_logging=False, loglevel=10, exchange=DEFAULT_EXCHANGE, exchange_type=EXCHANGE_TYPE): 

	return Logger(app_name='default', stdio_logging=False, loglevel=10, exchange=DEFAULT_EXCHANGE, exchange_type=EXCHANGE_TYPE) 



