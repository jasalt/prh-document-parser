""" TODO: add module docstring """
import traceback
from StringIO import StringIO
from multiprocessing import Process, Lock

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter


def debug_print(stdout_lock, msg):
    """ Prints a debugging message. """
    if stdout_lock is not None:
        with stdout_lock:
            print msg # TODO: use logging module


def process_file(filename):
    """ Loads and parses a pdf file.
        Raises exceptions to indicate parsing errors. """
    manager = PDFResourceManager(caching=True)
    output = StringIO()
    device = TextConverter(manager, output)
    interpreter = PDFPageInterpreter(manager, device)
    file_handle = file(filename, 'rb')

    for page in PDFPage.get_pages(file_handle, set(),
                                  caching=True, check_extractable=True):
        interpreter.process_page(page)
    file_handle.close()
    device.close()
    text = output.getvalue()
    output.close()

    # TODO: parse data from text instead of returning it as is
    return text


class Parser(Process):
    """ Process which extracts information from PDF files. """
    def __init__(self, job_queue, result_queue, stdout_lock=None):
        super(Parser, self).__init__()
        # This process is terminated when main process terminates
        self.daemon = True
        self.job_queue = job_queue
        self.result_queue = result_queue
        self.stdout_lock = stdout_lock
        debug_print(self.stdout_lock, "%s created." % self.name)


    def run(self):
        while True:
            # Get next job
            pdf_filepath = self.job_queue.get()
            if pdf_filepath is None:
                break

            # Report work status
            debug_print(self.stdout_lock, "%s is parsing %s..." % \
                                            (self.name, pdf_filepath))
            # Parse PDF file
            try:
                result = process_file(pdf_filepath)
                self.result_queue.put(result)
            except Exception:
                # TODO: use a better way to report parsing error?
                debug_print(self.stdout_lock, traceback.format_exc())

        debug_print(self.stdout_lock, "%s stopped." % self.name)