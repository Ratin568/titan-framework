
"""
Titan Logger - Console Handler
"""

import sys

from .base import BaseHandler
from ..formatter import TextFormatter


class ConsoleHandler(BaseHandler):
    def __init__(self, formatter=None, stream=None):
        super().__init__(formatter or TextFormatter())
        self.stream = stream or sys.stdout

    def emit(self, record):
        self.stream.write(self.formatter.format(record) + "\n")
        self.stream.flush()
