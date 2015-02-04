""" TODO: add module docstring """
import logging.handlers


class ProcessLogHandler(logging.Handler):
    """ Processes must pass their logging records
        to the main process using this handler. """
    def __init__(self, queue):
        super(ProcessLogHandler, self).__init__()
        self.queue = queue

    def emit(self, record):
        self.format(record)
        self.queue.put_nowait(record)


def handler_listener(queue):
    """ Listens log records from other processes and logs
        them in the main process. """
    while True:
        record = queue.get()
        if record is None:
            break
        logger = logging.getLogger(record.name)
        logger.handle(record)
    logging.debug("handler_listener closed.")
