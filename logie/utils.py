from tornado.web import URLSpec
import base64 
import os 
import time 
import datetime
import inspect
import yaml


def unpack(first, *rest):
    return first, rest

def include(prefix, module_path):
    module = __import__(module_path, globals(), locals(), fromlist=["*"])
    urls = getattr(module, 'urls')
    print urls
    final_urls = list()
    for url in urls:
        pattern = url.regex.pattern
        if pattern.startswith("/"):
            pattern = r"%s%s" % (prefix, pattern[1:])
        else:
            pattern = r"%s%s" % (prefix, pattern)
        final_urls.append(URLSpec(pattern, url.handler_class, kwargs=url.kwargs, name=url.name))
    return final_urls
    





# random id generator
def genid(n):
    return base64.urlsafe_b64encode(os.urandom(n)).replace('=', 'e')



def epoch():
    return int(time.time())


def formLocalTime(hour, mins, meridian): 
    now = datetime.datetime.now()
    return str(now.month) + '-' + str(now.day + 1) + '-' + str(now.year) + ' ' + str(hour) + ':' + str(mins) + ':00 ' + meridian


def local2UTC(t): 
    return int(time.mktime(time.strptime(t, '%m-%d-%Y %I:%M:%S %p')))


def expires(t):
    return int(time.mktime(time.strptime(t, '%m-%d-%Y %I:%M:%S %p'))) - int(time.time())


def timeCountdown(t):
    return int(time.mktime(time.strptime(t, '%m-%d-%Y %I:%M:%S %p'))) - int(time.time())


def localTime(): 
    return str(time.strftime("%m-%d-%Y %I:%M:%S %p", time.localtime()))



def newTimeAdd(t, a):
    return (t + a)


def newTimeSub(t, s):
    return (t - s)

def timeLeft(t):
    return int(t - time.time())

def whoami(): 
    return inspect.stack()[1][3]

def whoisdaddy(): 
    return inspect.stack()[2][3] 



def read_config_file(): 
    config_data = None
    # print 'cwd : '
    # print os.getcwd() 
    # print 'list of file : '
    # print os.listdir(os.getcwd())
    # print 'logie.conf exits so rnot : ', os.path.exists('logie.conf')
    try:
        with open('/usr/local/etc/logie.conf', 'rb') as f: 
            config_data = yaml.safe_load(f) 
    except Exception, e: 
        print 'exceptino opening logie.conf'
        print e
        
    return config_data





