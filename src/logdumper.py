import logging
from miscfuncs import to_expanded_string

class LogDumper(object):
    
    def __init__(self, logger):
        """Logging helper that that produces nicely formatted log entries

        Attach a Logger object to a LogDumper object, then use the LogDumper in
        place of (or in addtition to) the Logger.
        
        :param logger: A Logger instance
        :type logger: Logger
        """
        self.logger = logger
        
    def dump(self, level, *args):
        """Dump the given arguments at the given logging level

        :param level: The logging level
        :type level: Int
        :param args: Objects to be dumped
        :type args: List of objects
        """
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
        """Dump the given arguments at DEBUG level"""
        self.dump(logging.DEBUG, *args)

    def info(self, *args):
        """Dump the given arguments at INFO level"""
        self.dump(logging.INFO, *args)

    def warning(self, *args):
        """Dump the given arguments at WARNING level"""
        self.dump(logging.WARNING, *args)

    def error(self, *args):
        """Dump the given arguments at ERROR level"""
        self.dump(logging.ERROR, *args)

    def critical(self, *args):
        """Dump the given arguments at CRITICAL level"""
        self.dump(logging.CRITICAL, *args)

    
