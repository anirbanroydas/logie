import tornado.ioloop
import tornado.httpserver
import tornado.web
from tornado.options import define, options
# import yaml
# import uuid
# import os

print '[server.py] Entered Module'

print '[server.py] calling relative import settings'
from .settings import DEFAULT_APPINFO_APPNAME, DEFAULT_STORAGE_PATH, DEFAULT_APPLOG_PATH, DEFAULT_EXCHANGE, EXCHANGE_TYPE,\
    DEFAULT_LOGLEVELS, DEFAULT_APPINFO_WEBAPP, DEFAULT_APPLOG_APPEND, DEFAULT_STORAGE_APPEND, CONFIG_DATA
print '[server.py] read relatetive imnports settings.py'

print '[server.py] calling relative import apps.logger.log.py'
from .apps.logger.log import get_logger_logie, initiate_loggers
print '[server.py] read relatetive imnports apps.logger.log.py'

print '[server.py] calling relative import apps.logger.worker'
from .apps.logger.worker import RabbitLogWorker
print '[server.py] read relatetive imnports apps.logger.worker.py'

# import utils

# DEFAULT_APPINFO_APPNAME = 'defaut-logie-app'
# DEFAULT_STORAGE_PATH = '/usr/local/var/run'
# DEFAULT_APPLOG_PATH = '/usr/local/var/log/logie/logie.log'
# DEFAULT_EXCHANGE = 'logie_exchange'

# # Universal Default, doesn't depend on conf file
# EXCHANGE_TYPE = 'topic'

print '[server.py] calling initate_logger'
initiate_loggers()
print '[server.py] returned from initate_logger'
print '[server.py] calling get_logger_logie'
LOGGER = get_logger_logie(__name__)
print '[server.py] returned from get_logger_logie'



define("port", default=9091, help="run on the given port", type=int)



class Application(tornado.web.Application):

    def __init__(self, web_app):
        LOGGER.debug('inside Application init')
        
        # appinfo_web_app = CONFIG_DATA['appinfo']['web_app'] if CONFIG_DATA and 'appinfo' in CONFIG_DATA and 'web_app' in CONFIG_DATA['appinfo'] else DEFAULT_APPINFO_WEBAPP
        
        if web_app:
            from urls import urls
            from settings import settings

            tornado.web.Application.__init__(self, urls, **settings)

        if CONFIG_DATA:
            self.loglevels = CONFIG_DATA['loginfo']['loglevels'] if 'loginfo' in CONFIG_DATA and 'loglevels' in CONFIG_DATA['loginfo'] else DEFAULT_LOGLEVELS
            self.log_exchange = CONFIG_DATA['loginfo']['log_exchange'] if 'loginfo' in CONFIG_DATA and 'log_exchange' in CONFIG_DATA['loginfo'] else DEFAULT_EXCHANGE
            self.appinfo_app_name = CONFIG_DATA['appinfo']['app_name'] if 'appinfo' in CONFIG_DATA and 'app_name' in CONFIG_DATA['appinfo'] else DEFAULT_APPINFO_APPNAME
            self.storage_path = CONFIG_DATA['storage']['path'] if 'storage' in CONFIG_DATA and 'path' in CONFIG_DATA['storage'] else DEFAULT_STORAGE_PATH
            # self.storage_type = config_data['storage']['type'] if 'storage' in config_data and 'type' in config_data['storage'] else DEFAULT_STORAGE_TYPE
            self.storage_append = CONFIG_DATA['storage']['file_append'] if 'storage' in CONFIG_DATA and 'file_append' in CONFIG_DATA['storage'] else DEFAULT_STORAGE_APPEND
            self.applog_path = CONFIG_DATA['applog']['path'] if 'applog' in CONFIG_DATA and 'path' in CONFIG_DATA['applog'] else DEFAULT_APPLOG_PATH
            # self.applog_type = config_data['applog']['type'] if 'applog' in config_data and 'type' in config_data['applog'] else DEFAULT_APPLOG_TYPE
            self.applog_append = CONFIG_DATA['applog']['file_append'] if 'applog' in CONFIG_DATA and 'file_append' in CONFIG_DATA['applog'] else DEFAULT_APPLOG_APPEND
            # self.separate = config_data['loginfo']['separate'] if 'loginfo' in config_data and 'separate' in config_data['loginfo'] else DEFAULT_FILE_SEPARATION


        else:
            self.loglevels = DEFAULT_LOGLEVELS
            self.log_exchange = DEFAULT_EXCHANGE
            self.appinfo_app_name = DEFAULT_APPINFO_APPNAME
            self.storage_path = DEFAULT_STORAGE_PATH
            # self.storage_type = DEFAULT_STORAGE_TYPE
            self.storage_append = DEFAULT_STORAGE_APPEND
            self.applog_path = DEFAULT_APPLOG_PATH
            # self.applog_type = DEFAULT_APPLOG_TYPE
            self.applog_append = DEFAULT_APPLOG_APPEND
            # self.separate = DEFAULT_FILE_SEPARATION

        if self.storage_path.endswith('/'):
            self.storage_path = self.storage_append[:-1]

        self.loglevels = self.process_log_levels(self.loglevels)
        
        # initiate_worker_logger()
        self.workers = self.start_log_workers()



    def process_log_levels(self, levels):
        LOGGER.debug('inside process_log_levels')
        LOGGER.debug('loglevls : %s ', levels)
        loglevels = []

        for item in levels:
            item = item.strip().lower()

            if item == 'debug' or item == 'd':
                loglevels.append('DEBUG')

            elif item == 'info' or item == 'i':
                loglevels.append('INFO')

            elif item == 'warning' or item == 'w':
                loglevels.append('WARNING')

            elif item == 'error' or item == 'e':
                loglevels.append('ERROR')

            elif item == 'critical' or item == 'c':
                loglevels.append('CRITICAL')

            elif item == 'all' or item == 'a':
                loglevels.append('ALL')

        return loglevels



    def start_log_workers(self):
        LOGGER.debug('inside start_log_workers')
        LOGGER.debug('loglevls : %s ', self.loglevels)
        workers = dict()

        for item in self.loglevels:
            LOGGER.debug('for loglevel : %s ' % item)
            LOGGER.debug('initialize logworker client')
            workers[item] = RabbitLogWorker(exchange=self.log_exchange,
                                            exchange_type=EXCHANGE_TYPE,
                                            exchange_durability=True,
                                            queue_binding_key=self.appinfo_app_name + '.' + item,
                                            queue_durability=True,
                                            queue_exclusivity=False,
                                            queue_auto_delete=False,
                                            queue='queue-' + self.appinfo_app_name + '-' + item
                                            )
            LOGGER.debug('starting rabbitlogworker')
            workers[item].start()
            LOGGER.debug('logworker started successufley')

        return workers









def main():
    # Parse the command line arguements
    tornado.options.parse_command_line()

    port = None

    # read the conf file
    # config_data = read_config_file()
    # print 'len(config_data) : ', len(config_data)

    appinfo_web_app = CONFIG_DATA['appinfo']['web_app'] if 'appinfo' in CONFIG_DATA and 'web_app' in CONFIG_DATA['appinfo'] else DEFAULT_APPINFO_WEBAPP
    app = Application(appinfo_web_app)

    if options.port == 9091 and 'net' in CONFIG_DATA and 'port' in CONFIG_DATA['net']:
        port = CONFIG_DATA['net']['port']
    else:
        port = options.port

    if appinfo_web_app:
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(port)
        LOGGER.info('[server.main] Starting Webapp at http://127.0.0.1:%s', port)

    try:
        LOGGER.info("\n[server.main] Server Started.\n")

        tornado.ioloop.IOLoop.current().start()

    except KeyboardInterrupt:
        LOGGER.error('\n[server.main] EXCEPTION KEYBOARDINTERRUPT INITIATED\n')
        LOGGER.info("[server.main] Stopping Server....")
        LOGGER.info(
            '[server.main] closing all websocket connections objects and corresponsding pika client objects')
        LOGGER.info("\n[server.main] Server Stopped.")


if __name__ == "__main__":
    main()
