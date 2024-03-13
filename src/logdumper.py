import logging
from miscfuncs import to_expanded_string

class LogDumper(object):
    
    def __init__(self, logger):
        self.logger = logger
        
    def dump(self, level, *args):
        if not self.logger.isEnabledFor(level):
            return
        dumplines = list()
        for arg in args:
            dumplines.append(to_expanded_string(arg))
        dumplines = self._expand_lines(dumplines)
        for dumpline in dumplines:
            self.logger.log(level,dumpline)

    def _expand_lines(self,inlines):
        outlines = list()
        for line in inlines:
            if line is None:
                outlines.append("(None)")
            else:
                outlines.extend(line.split("\n"))
        return outlines

    def debug(self, *args):
        self.dump(logging.DEBUG, *args)

    def info(self, *args):
        self.dump(logging.INFO, *args)

    def warning(self, *args):
        self.dump(logging.WARNING, *args)

    def error(self, *args):
        self.dump(logging.ERROR, *args)

    def critical(self, *args):
        self.dump(logging.CRITICAL, *args)

    
