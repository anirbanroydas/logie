"""
The worker module provides interface for the rabbitmq client.

It provides classes to create pika clients to connect to rabbitmq broker server, interact with
and publish/subscribe to rabbitmq via creating channels, methods to publish, subscribe/consume, 
stop consuming, start publishing, start connection, stop connection, create channel, close channel, 
acknowledge delivery by publisher, acknowledge receiving of messages by consumers, send basic ack, 
basic cancel requests and also add callbacks for various other events.
"""

print '[worker.py] Entered Module'

import pika.adapters
import pika
import uuid
import msgpack


print '[worker.py] calling relative imnport logie.settings'
from logie.settings import DEFAULT_EXCHANGE, EXCHANGE_TYPE, DEFAULT_PORT
print '[worker.py] returning from relative imnport logie.settings'

print '[worker.py] calling relative imnport logie.logger.log.py'
from .log import get_file_logger, set_adapter, get_logger_logie, initiate_loggers
print '[worker.py] returning from  relative imnport logie.logger.log.py'

# DEFAULT_EXCHANGE = 'logie_exchange'

# # Universal Default, doesn't depend on conf file 
# EXCHANGE_TYPE = 'topic'

# # Universal RabbitMQ PORT 
# DEFAULT_PORT = 5672



# EXCHANGE = ''
# EXCHANGE_TYPE = 'topic'
# PORT = 5672

print '[worker.py] calling initate_logger'
initiate_loggers()
print '[worker.py] retrned from initiate_loggers'

print '[worker.py] calling get_logger_logie'
LOGGER = get_logger_logie(__name__)
print '[worker.py] retrned from get_logger_logie'

print '[worker.py] calling get_file_logger'
FILE_LOGGER = get_file_logger()
print '[worker.py] retrned from get_file_logger'



def initiate_worker_logger(): 
    global FILE_LOGGER 

    FILE_LOGGER = get_file_logger()





class RabbitLogWorker(object):
    """
    This is a RabbitMQ Client using the TornadoConnection Adapter that will
    handle unexpected interactions with RabbitMQ such as channel and connection closures.

    If RabbitMQ closes the connection, it will reopen it. You should
    look at the output, as there are limited reasons why the connection may
    be closed, which usually are tied to permission related issues or
    socket timeouts.

    If the channel is closed, it will indicate a problem with one of the
    commands that were issued and that should surface in the output as well.

    It alos uses delivery confirmations and illustrates one way to keep track of
    messages that have been sent and if they've been confirmed by RabbitMQ.

    """

    def __init__(self, host='localhost', username='guest', password='guest', credentials=None, params=None,
                 exchange=None, exchange_type=None, exchange_durability=True,
                 queue=None, queue_binding_key=None, queue_durability=False, queue_exclusivity=False, queue_auto_delete=False):
        """Create a new instance of the consumer class, passing in the AMQP
        URL used to connect to RabbitMQ.

        :param credentials: credentials to connect to rabbitmq broker server
        :type credentials: pika.credentials.PlainCredentials
        :param params: connection paramaters used to connect with rabbitmq broker server
        :type params: pika.connection.ConnectionParameters
        :param queue: queue to be created after a channel is established which will be bound to an exchange
        :type queue: string - random long base64 url safe encoded string

        """


        self._connection = None
        self._connected = False
        self._connecting = False
        self._channel = None
        self._closing = False
        self._closed = False
        self._consumer_tag = None
        self._deliveries = []
        self._acked = 0
        self._nacked = 0
        self._message_number = 0
        self._credentials = credentials if credentials else pika.PlainCredentials(username, password)
        self._parameters = params if params else pika.ConnectionParameters(host=host,
                                                                           port=DEFAULT_PORT,
                                                                           virtual_host='/',
                                                                           credentials=self._credentials)
        self._queue = queue if queue else 'queue-' + str(uuid.uuid4())
        self._exchange = exchange if exchange else DEFAULT_EXCHANGE
        self._exchange_type = exchange_type if exchange_type else EXCHANGE_TYPE
        self._exchange_durability = exchange_durability
        self._queue_binding_key = queue_binding_key
        self._queue_durability = queue_durability
        self._queue_exclusivity = queue_exclusivity
        self._queue_auto_delete = queue_auto_delete
        self.websocket = None
        self._status = 0
        # self._person = person
        self._clientid = None
        self._participants = 0


    def connect(self):
        """This method connects to RabbitMQ via the Torando Connectoin Adapter, returning the 
        connection handle.

        When the connection is established, the on_connection_open method
        will be invoked by pika.

        :return: Returns a pika connection object which is a tornado connection object to rabbitmq server
        :rtype: pika.adapters.TornadoConnection

        """


        if self._connecting:
            LOGGER.warning('[RabbitLogClient] Already connecting to RabbitMQ')
            return

        LOGGER.info('[RabbitLogClient] Connecting to RabbitMQ on localhost:5672, Object: %s ' % self)
        self._connecting = True



        return pika.adapters.TornadoConnection(parameters=self._parameters,
                                               on_open_callback=self.on_connection_opened,
                                               stop_ioloop_on_close=False)





    def on_connection_opened(self, connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.

        :param connection: connection object created
        :type connection: pika.adapters.TornadoConnection

        """

        LOGGER.info('[RabbitLogClient] Rabbitmq connection opened : %s ' % connection)

        self._status = 1
        self._connected = True
        self._connection = connection

        self.add_on_connection_close_callback()
        self.open_channel()



    def add_on_connection_close_callback(self):
        """This method adds an on close callback that will be invoked by pika
        when RabbitMQ closes the connection to the publisher unexpectedly.

        """

        self._connection.add_on_close_callback(callback_method=self.on_connection_closed)




    def on_connection_closed(self, connection, reply_code, reply_text):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param  connection: The closed connection obj
        :type connection: pika.connection.Connection
        :param reply_code: The server provided reply_code if given
        :type reply_code: int 
        :param reply_text: The server provided reply_text if given
        :type reply_text: str 

        """

        LOGGER.warning(
            '[RabbitLogClient] Rabbitmq connection closed unexpectedly : %s ' % connection)

        self._channel = None
        self._connecting = False
        self._connected = False
        self._status = 0
        if self._closing:
            LOGGER.warning('[RabbitLogClient] connection already closing')
            return

        else:
            LOGGER.info("Connection closed, reopening in 5 seconds: reply_code : [%d] : reply_text : %s " % (
                reply_code, reply_text))

            self._connection.add_timeout(5, self.reconnect)

 

    def reconnect(self):
        """Will be invoked by the IOLoop timer if the connection is
        closed. See the on_connection_closed method.

        """

        LOGGER.info('[RabbitLogClient] Reconnecting to rabbitmq')

        if not self._closing:
            # Create a new connection
            self._connection = self.connect()



    def close_connection(self):
        """This method closes the connection to RabbitMQ."""

        if self._closing:
            LOGGER.warning('[RabbitLogClient] connection is already closing...')
            return

        self._closing = True

        self._connection.close()

        self._connecting = False
        self._connected = False

        if self._channel:
            self._channel = None
        if self._connection:
            self._connection = None
        if self._consumer_tag:
            self._consumer_tag = None
        if self._queue:
            self._queue = None
        if self.websocket:
            self.websocket = None

        self._parameters = None
        self._credentials = None
        self._status = 0
        self._closed = True
        # self._person = None

        LOGGER.info('[RabbitLogClient] rabbitmq connection cosed')


    def open_channel(self):
        """Open a new channel with RabbitMQ by issuing the Channel.Open RPC
        command. When RabbitMQ responds that the channel is open, the
        on_channel_open callback will be invoked by pika.

        """

        LOGGER.info('[RabbitLogClient] Creating a new channel for connection : %s ' %
                    self._connection)

        self._channel = self._connection.channel(on_open_callback=self.on_channel_open)



    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        Since the channel is now open, we'll declare the exchange to use.

        :param channel: The channel object
        :type channel: pika.channel.Channel 

        """

        LOGGER.info('[RabbitLogClient] Channel opened : %s ' % channel)

        self._status = 2

        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange()



    def close_channel(self):
        """Call to close the channel with RabbitMQ cleanly by issuing the
        Channel.Close RPC command.

        """

        LOGGER.info('[RabbitLogClient] Closing the channel... ')

        self._status = 1

        self._channel.close()

        if self._channel:
            LOGGER.info('[RabbitLogClient] Channel closed : %s ' % self._channel)
            self._channel = None

        else:
            LOGGER.info('[RabbitLogClient] Channel closed')




    def add_on_channel_close_callback(self):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.

        """

        self._channel.add_on_close_callback(self.on_channel_closed)



    def on_channel_closed(self, channel, reply_code, reply_text):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.

        :param channel: The closed channel
        :type channel: pika.channel.Channel
        :param reply_code: The numeric reason the channel was closed
        :type reply_code: int 
        :param reply_text: The text reason the channel was closed
        :type reply_text: str 

        """

        LOGGER.info("Channel %i was closed: reply_code : [%d] reply_text : %s " % (
            channel, reply_code, reply_text))

        self._status = 1

        self.close_connection()



    def setup_exchange(self):
        """Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
        command. When it is complete, the on_exchange_declareok method will
        be invoked by pika.

        """


        LOGGER.info('[RabbitLogClient] Declaring exchange : %s ' % self._exchange)
        self._channel.exchange_declare(exchange=self._exchange,
                                       exchange_type=self._exchange_type,
                                       durable=self._exchange_durability,
                                       auto_delete=False,
                                       nowait=False,
                                       callback=self.on_exchange_declareok)




    def on_exchange_declareok(self, frame):
        """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.

        :param frame: Exchange.DeclareOk response frame
        :type frame: pika.Frame.Method

        """

        LOGGER.info('[RabbitLogClient] Exchange declared')

        self._status = 3

        self.setup_queue()



    def setup_queue(self):
        """Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declareok method will
        be invoked by pika.

        """


        LOGGER.info('[RabbitLogClient] Declaring queue : for channel object : %s ' % self._channel)

        self._channel.queue_declare(queue=self._queue,
                                    durable=self._queue_durability,
                                    exclusive=self._queue_exclusivity,
                                    auto_delete=self._queue_auto_delete,
                                    nowait=False,
                                    arguments=None,
                                    callback=self.on_queue_declareok)




    def on_queue_declareok(self, method_frame):
        """Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. mand is complete, the on_bindok method will
        be invoked by pika.

        :param  method_frame: The Queue.DeclareOk frame
        :type method_frame: pika.frame.Method

        """

        LOGGER.info('[RabbitLogClient] Queue declared')

        self._status = 4

        self.bind_queue(self._queue_binding_key)



    def bind_queue(self, binding_key):
        """In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command.

        :param  binding_key: The routing_key argument
        :type binding_key: string

        """


        LOGGER.info('[RabbitLogClient] Binding %s to %s with %s ' %
                    (self._exchange, self._queue, binding_key))

        self._channel.queue_bind(callback=self.on_bindok,
                                 queue=self._queue,
                                 exchange=self._exchange,
                                 routing_key=binding_key,
                                 nowait=False,
                                 arguments=None)




    def on_bindok(self, unused_frame):
        """Invoked by pika when the Queue.Bind method has completed. At this
        point we will start consuming messages by calling start_consuming
        which will invoke the needed RPC commands to start the process.
        It will also set channel for publishing.

        :param  unused_frame: The Queue.BindOk response frame
        :type unused_frame: pika.frame.Method

        """

        LOGGER.info('[RabbitLogClient] Queue bound')

        self._status = 5

        self.start_consuming()






    def start_consuming(self):
        """This method sets up the consumer by first calling
        add_on_cancel_callback so that the object is notified if RabbitMQ
        cancels the consumer. It then issues the Basic.Consume RPC command
        which returns the consumer tag that is used to uniquely identify the
        consumer with RabbitMQ. We keep the value to use it when we want to
        cancel consuming. The on_message method is passed in as a callback pika
        will invoke when a message is fully received.

        """


        LOGGER.info('[RabbitLogClient] Started Consuming - Issuing consumer related RPC commands')

        self.add_on_cancel_callback()

        self._consumer_tag = self._channel.basic_consume(consumer_callback=self.on_message,
                                                         queue=self._queue,
                                                         no_ack=False,
                                                         exclusive=True,
                                                         )
        self._status = 7

        LOGGER.info('[RabbitLogClient] self._status ==7 now')
        LOGGER.info(
            '[RabbitLogClient] rabbit client can now publish/consume msessag.\nSending first msg to websocket...')





    def add_on_cancel_callback(self):
        """Add a callback that will be invoked if RabbitMQ cancels the consumer
        for some reason. If RabbitMQ does cancel the consumer,
        on_consumer_cancelled will be invoked by pika.

        """

        self._channel.add_on_cancel_callback(callback=self.on_consumer_cancelled)



    def on_consumer_cancelled(self, method_frame):
        """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.

        :param  method_frame: The Basic.Cancel frame
        :type method_frame: pika.frame.Method

        """


        LOGGER.info(
            '[RabbitLogClient] Consumer was cancelled remotely, shutting down.... sent method_frame %s ' % method_frame)

        if self._channel:
            LOGGER.info('[RabbitLogClient] initating closing of channel')
            self.close_channel()



    def on_message(self, unused_channel, basic_deliver, properties, body):
        """Invoked by pika when a message is delivered from RabbitMQ. The
        channel is passed for your convenience. The basic_deliver object that
        is passed in carries the exchange, routing key, delivery tag and
        a redelivered flag for the message. The properties passed in is an
        instance of BasicProperties with the message properties and the body
        is the message that was sent.

        :param  unused_channel: The channel object
        :type unused_channel: pika.channel.Channel
        :param basic_deliver: The basic delivery object passed
        :type basic_deliver: pika.Spec.Basic.Deliver
        :param properties: The basic properties used to publish the message
        :type properties: pika.Spec.BasicProperties
        :param  body: The message body
        :type body: str|unicode

        """


        LOGGER.info('[RabbitLogClient] Received message # %s from %s : %s ' %
                    (basic_deliver.delivery_tag, properties.app_id, body))

        msgpack_decoded_body = msgpack.unpackb(body, encoding='utf-8')

        # acknowledge the messge received
        self.acknowledge_message(basic_deliver.delivery_tag)

        # log the msg for real
        self.handleLogging(msgpack_decoded_body)
        
        if self.websocket:
            self.websocket.send(body)




    def acknowledge_message(self, delivery_tag):
        """Acknowledge the message delivery from RabbitMQ by sending a
        Basic.Ack RPC method for the delivery tag.

        :param delivery_tag: The delivery tag from the Basic.Deliver frame
        :type delivery_tag: int 

        """


        LOGGER.info('[RabbitLogClient] Acknowledging message %i ' % delivery_tag)

        self._channel.basic_ack(delivery_tag)





    def handleLogging(self, msg): 

        loglevel = msg['loglevel'] 
        adapter = set_adapter(FILE_LOGGER, msg)

        if loglevel == 'NOTSET':
            adapter.log(0, '')

        elif loglevel == 'DEBUG':
            adapter.debug('')

        elif loglevel == 'INFO': 
            adapter.info('') 

        elif loglevel == 'WARNING': 
            adapter.warning('')

        elif loglevel == 'ERROR': 
            adapter.error('') 

        elif loglevel == 'CRITICAL': 
            adapter.critical('')





    def stop_consuming(self):
        """Tell RabbitMQ that you would like to stop consuming by sending the
        Basic.Cancel RPC command.

        """

        LOGGER.info('[RabbitLogClient] stopping consuming....')

        if self._channel:
            LOGGER.info('[RabbitLogClient] Sending a Basic.Cancel RPC command to RabbitMQ')

            self._channel.basic_cancel(callback=self.on_cancelok,
                                       consumer_tag=self._consumer_tag)




    def on_cancelok(self, unused_frame):
        """This method is invoked by pika when RabbitMQ acknowledges the
        cancellation of a consumer. At this point we will close the channel.
        This will invoke the on_channel_closed method once the channel has been
        closed, which will in-turn close the connection.

        :param  unused_frame: The Basic.CancelOk frame
        :type unused_frame: pika.frame.Method

        """


        LOGGER.info('[RabbitLogClient] RabbitMQ acknowledged the cancellation of the consumer')

        if self._consumer_tag:
            self._consumer_tag = None

        self.close_channel()
        self.close_connection()



    def start(self):
        """Run the example consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.

        """

        LOGGER.info('[RabbitLogClient] starting the rabbitmq connection')

        self._connection = self.connect()
        # self._connection.ioloop.start()



    def stop(self):
        """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.

        """


        LOGGER.info('[RabbitLogClient] Stopping RabbitLogClient object... : %s ' % self)

        self.stop_consuming()

        LOGGER.info('[RabbitLogClient] RabbitLogClient Stopped')


    @property
    def status(self):
        """Gives the status of the RabbitLogClient Connection.


        :return: Returns the current status of the connection
        :rtype: self._status

        """


        return self._status


