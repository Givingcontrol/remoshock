import os
import sys

class HidePrintIfNotVerbose:
    def __init__(self, verbose):
        self.verbose = verbose


    def __enter__(self):
        if not self.verbose:
            self.__real_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')


    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        if not self.verbose:
            try:
                sys.stdout.close()
            finally:
                sys.stdout = self.__real_stdout
