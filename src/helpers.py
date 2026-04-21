
# Contains helper functions n stuff
import traceback,logging

def log_exc(logger:logging.Logger,e:Exception):
    for i in "".join(traceback.format_exception(e)).splitlines():
        logger.error(i)