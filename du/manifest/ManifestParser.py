import sys
from du.manifest.Exceptions import *
import traceback


class ManifestParser:
    """
    Manifest script parser
    """

    @classmethod
    def executeString(cls, source, scriptLocals):
        """
        Execute a script, and provide a detailed exception

        @param source Script source
        @param scriptLocals Script locals
        """

        # Execute script
        try:
            exec(source, scriptLocals)
        except SyntaxError as e:
            detail = e.args[0]
            lineNumber = e.lineno
        except Exception as e:
            detail = e.args[0]
            cl, exc, tb = sys.exc_info()
            lineNumber = traceback.extract_tb(tb)[-1][1]
        else:
            return

        raise ManifestParseError("at line %d: %s" % (lineNumber, detail))
