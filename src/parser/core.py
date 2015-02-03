""" TODO: add module docstring """
import os
import fnmatch
import threading
from multiprocessing import Queue, Lock, cpu_count

from pdfparser import Parser, debug_print


def path_iterator(search_path, file_pattern):
    """ Iterates recursively all files that match file_pattern. """
    for dirpath, _, filenames in os.walk(search_path):
        for filename in fnmatch.filter(filenames, file_pattern):
            yield os.path.join(dirpath, filename)


def result_collector(result_queue, stdout_lock=None):
    """ Stores result from result_queue to a database. """

    # TODO: connect to database

    while True:
        result = result_queue.get()
        if result is None:
            break

        # TODO: store result in database

    # TODO: close connection to database
    debug_print(stdout_lock, "result_collector stopped.")


def parse(search_path, num_parsers=cpu_count()):
    """ Finds and parses all PDF files in search_path.
        Results are stored in a database. """
    stdout_lock = Lock()
    job_queue = Queue(num_parsers)
    result_queue = Queue()

    # Create parser processes
    parsers = []
    for _ in xrange(num_parsers):
        parser = Parser(job_queue, result_queue, stdout_lock)
        parser.start()
        parsers.append(parser)

    # Start result collector
    collector = threading.Thread(target=result_collector,
                                 args=(result_queue, stdout_lock))
    collector.start()

    # Recursively search pdf files in search_path and put them in job queue
    for filepath in path_iterator(search_path, "*.pdf"):
        job_queue.put(filepath)

    # Send stop commands to parsers and result collector
    for _ in xrange(num_parsers):
        job_queue.put(None)
    result_queue.put(None)

    # Join all parser processes
    for parser in parsers:
        parser.join()

    debug_print(stdout_lock, "All parsers joined.")

    # Join result collector thread
    collector.join()

    debug_print(stdout_lock, "Parsing done.")


if __name__ == '__main__':
    pass # TODO: get command line arguments and use parse function
