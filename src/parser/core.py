# -*- coding: utf-8 -*-
""" TODO: add module docstring """
import os
import fnmatch
import logging
import threading
from multiprocessing import Queue, cpu_count

from loggingutil import handler_listener
from pdfparser import Parser

logger = logging.getLogger(__name__)


def path_iterator(search_path, file_pattern):
    """ Iterates recursively all files that match file_pattern. """
    for dirpath, _, filenames in os.walk(search_path):
        for filename in fnmatch.filter(filenames, file_pattern):
            yield os.path.join(dirpath, filename)


def result_collector(result_queue):
    """ Stores result from result_queue to a database. """

    # TODO: connect to database

    while True:
        result = result_queue.get()
        if result is None:
            break

        # TODO: store result in database
        with open(result[0].split('.')[0]+'.txt', 'w') as handle:
            handle.write(repr(result[1]))

    # TODO: close connection to database
    logger.debug("result_collector stopped.")


def parse(search_path, num_parsers=cpu_count(), process_loglevel=logging.DEBUG):
    """ Finds and parses all PDF files in search_path.
        Results are stored in a database. """
    logger.info("Parsing pdf files from '%s' with %d parsers.",
                search_path, num_parsers)

    job_queue = Queue(num_parsers) # Queue for pdf file names
    result_queue = Queue()         # Queue for parsing results
    log_queue = Queue()            # Queue for logging

    # Create parser processes
    parsers = []
    for _ in xrange(num_parsers):
        parser = Parser(job_queue, result_queue, log_queue, process_loglevel)
        parser.start()
        parsers.append(parser)

    # Start result collector and process log listener
    collector = threading.Thread(target=result_collector, args=(result_queue,))
    collector.start()
    loglistener = threading.Thread(target=handler_listener, args=(log_queue,))
    loglistener.start()

    # Recursively search pdf files in search_path and put them in the job queue
    num_files = 0
    for filepath in path_iterator(search_path, "*.pdf"):
        job_queue.put(filepath)
        num_files += 1

    # Send stop commands to parsers
    for _ in xrange(num_parsers):
        job_queue.put(None)

    # Join all parser processes
    for parser in parsers:
        parser.join()
    logger.debug("All parsers joined.")

    # Send rest of the stop commands
    result_queue.put(None)
    log_queue.put(None)

    # Join result collector thread
    collector.join()

    logger.info("Parsed %d pdf files.", num_files)


def __main__():
    import optparse
    loglevels = { 'debug':    logging.DEBUG,
                  'info':     logging.INFO,
                  'warning':  logging.WARNING,
                  'error':    logging.ERROR,
                  'critical': logging.CRITICAL }

    parser = optparse.OptionParser(usage="usage: %prog [options] searchpath")
    parser.add_option("-f", "--logfile", dest="logfile",
                      help="file name for program log [default: %default]")
    parser.add_option("-l", "--level", dest="level", default="warning",
                      help="logging level (debug, info, warning, error, " + \
                            "critical) [default: %default]")
    options, args = parser.parse_args()

    if len(args) == 0:
        print "Error: searchpath argument is missing."
        parser.print_help()
        return

    # Initialize logging
    loglevel = loglevels.get(options.level, logging.WARNING)
    logging.basicConfig(filename=options.logfile, level=loglevel)

    # Warn about invalid logging level
    if not options.level in loglevels:
        logger.warning("Invalid loglevel option: %s", options.level)

    # Start parsing
    for arg in args:
        parse(arg, process_loglevel=loglevel)

if __name__ == '__main__':
    __main__()
