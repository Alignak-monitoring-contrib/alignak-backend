import logging

root = logging.getLogger()
logging.basicConfig()


class Log(object):

    def __init__(self):

        self.namespace = "{modulename}.{classname}".format(
            classname=self.__class__.__name__,
            modulename=self.__module__
        )
        self.log = logging.getLogger(self.namespace)

