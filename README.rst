logie
======

It is a log server which uses AMQP protocol and RabbitMQ message broker and written using python and Tornado framework.

Documentation

--------------

**Link :** http://logie.readthedocs.io/en/latest/


Project Home Page

--------------------

**Link :** https://pypi.python.org/pypi/logie



Details

--------


:Author: Anirban Roy Das
:Email: anirban.nick@gmail.com
:Copyright(C): 2016, Anirban Roy Das <anirban.nick@gmail.com>

Check ``logie/LICENSE`` file for full Copyright notice.




Overview
---------

logie is a log server which can be used by any python based program to log in a multiprocessing environment.

User needs to import logie as a library and call the logger and start logging.



Technical Specs
----------------

:Tornado: Async Python Web Library + Web Server
:Rabbitmq: AMQP message broker



Features
---------

* Web App (Added Extra)
* multiprocessing logging




Installation
------------

Prerequisites
~~~~~~~~~~~~~

1. python 2.7+
2. tornado


Install
~~~~~~~
::

        $ pip install logie

If above dependencies do not get installed by the above command, then use the below steps to install them one by one.

 **Step 1 - Install pip**

 Follow the below methods for installing pip. One of them may help you to install pip in your system.

 * **Method 1 -**  https://pip.pypa.io/en/stable/installing/

 * **Method 2 -** http://ask.xmodulo.com/install-pip-linux.html

 * **Method 3 -** If you installed python on MAC OS X via ``brew install python``, then **pip** is already installed along with python.


 **Step 2 - Install tornado**
 ::

         $ pip install tornado

 **Step 3 - Configure logie**
 ::

        ``/usr/local/etc/logie.conf``






Usage
-----

After having installed logie, just run the following commands to use it:


* **Start uberNow Applcation**
  ::

          $ logie [options]

  - **Options**

    :--port: Port number where the uberNow app will start


  - **Example**
    ::

          # Starting the server
          $ logie --port=9191

          # Starting the server with custom log path
          $ logie --port=9191       
  
* **Stop logie**



  Click ``Ctrl+C`` to stop the server.


* **More Details** 

  Please follow the documentation for more usage details. Documentation link is `this <http://logie.readthedocs.io/en/latest/>`_.

Todo
-----

1. Add Blog post regarding this topic.


