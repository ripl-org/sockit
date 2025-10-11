"""
Extends the built-in logging module
"""
import logging    
class Log(object):
    def __init__(self, *names):
        self.name = ":".join(names)
        self.log = logging.getLogger(self.name)
    def debug(self, *message, sep=" "):
        self.log.debug(" {}".format(sep.join(map(str, message))))
    def error(self, *message, sep=" "):
        self.log.error(" {}".format(sep.join(map(str, message))))
    def info(self, *message, sep=" "):
        self.log.info(" {}".format(sep.join(map(str, message))))
    def warn(self, *message, sep=" "):
        self.log.warn(" {}".format(sep.join(map(str, message))))
