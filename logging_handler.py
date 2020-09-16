import logging
import logging.handlers
import queue
import sys
import time

g_queue_listner = None

class HTTPCustomHandler(logging.handlers.HTTPHandler):
    def emit(self, record):
        """
        Emit a record
        Send the record to the Web Server as json.
        """
        try:
            import requests
            import json
            from datetime import datetime
            api_url = self.host + self.url
            data_dict_org = self.mapLogRecord(record)
            data_dict = {"createdDate": datetime.fromtimestamp(data_dict_org['created']).isoformat(),
                         'logLevel': data_dict_org['levelname'], 'pathName': data_dict_org['pathname'],
                         'modeuleName': data_dict_org['module'], 'excInfo': data_dict_org['exc_info'],
                         'excText': data_dict_org['exc_text'], 'stackInfo': data_dict_org['stack_info'],
                         'lineNumber': data_dict_org['lineno'], 'functionName': data_dict_org['funcName'],
                         'processName': data_dict_org['processName'], 'message': data_dict_org['message'],
                         'other_custom_globals': 'CUSTOM'}

            data_str = json.dumps(data_dict)
            if self.method == 'POST':
                requests.post(api_url, json=json.loads(data_str), verify=False)
        except Exception:
            self.handleError(record)


def get_logger():
    global g_queue_listner

    logger = logging.getLogger('my_logger')
    if len(logger.handlers) > 0:
        return logger

    logging.raiseExceptions = False
    formatter = logging.Formatter(
        "%(levelname)s    %(asctime)s    module:%(module)s    line_no:%(lineno)d    %(message)s",
        '%Y-%m-%dT%H:%M:%S%z')
    logger.setLevel(logging.DEBUG)
    logger.propagate  = False
    log_queue = queue.Queue(-1)
    queue_handler = logging.handlers.QueueHandler(log_queue)
    logger.addHandler(queue_handler)

    file_handler = logging.FileHandler('server.log')
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    api_url = 'http://localhost:9200/logging'
    es_log_handler = HTTPCustomHandler(api_url, '/logs', method='POST')

    g_queue_listner = logging.handlers.QueueListener(log_queue, console_handler, file_handler, es_log_handler)
    g_queue_listner.start()

    return logger

def reset_logger_queue():
    if g_queue_listner:
        g_queue_listner.stop()
        g_queue_listner.start()

if __name__=='__main__':
    logger1 = get_logger()
    for i in range(100):
        logger1.info('This is dummy message : {}'.format(i))
        time.sleep(1)


