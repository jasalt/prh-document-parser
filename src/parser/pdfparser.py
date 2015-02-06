# -*- coding: utf-8 -*-
""" PDF parsing and information extraction. """
import logging
import traceback
from StringIO import StringIO
from multiprocessing import Process

from loggingutil import ProcessLogHandler
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter

from parsertypes import registerlog


def process_file(filename):
    """ Loads and parses a pdf file.
        Raises exceptions to indicate parsing errors. """
    manager = PDFResourceManager(caching=True)
    output = StringIO()
    device = TextConverter(manager, output)
    interpreter = PDFPageInterpreter(manager, device)
    file_handle = file(filename, 'rb')

    pages = PDFPage.get_pages(file_handle,
                              set(),
                              caching=True,
                              check_extractable=True)

    for page in pages:
        interpreter.process_page(page)

    # Close streams and handles
    file_handle.close()
    device.close()
    text = output.getvalue()
    output.close()

    data = None
    available_parsers = [registerlog.parser]
    for can_parse, parse in available_parsers:
        if can_parse(text):
            data = parse(text)
            break

    return (filename, data)


class Parser(Process):
    """ Process that extracts information from PDF files. """
    def __init__(self, job_queue, result_queue, log_queue, loglevel=logging.DEBUG):
        super(Parser, self).__init__()
        # This process is terminated when main process terminates
        self.daemon = True
        self.job_queue = job_queue
        self.result_queue = result_queue
        self.log_queue = log_queue
        self.loglevel = loglevel
        logger = logging.getLogger(__name__)
        logger.setLevel(loglevel)
        logger.debug("%s created.", self.name)


    def run(self):
        logger = logging.getLogger(__name__)
        logger.addHandler(ProcessLogHandler(self.log_queue))
        logger.setLevel(self.loglevel)
        while True:
            # Get next job
            pdf_filepath = self.job_queue.get()
            if pdf_filepath is None:
                break

            # Report work status
            logger.info("%s is parsing %s...", self.name, pdf_filepath)

            # Parse PDF file
            try:
                result = process_file(pdf_filepath)
                self.result_queue.put(result)
            except Exception:
                logger.error(traceback.format_exc())

        logger.debug("%s stopped.", self.name)
