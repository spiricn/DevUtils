import os


class Preprocessor:
    """
    Class used to preprocess Docker.in files
    """

    @staticmethod
    def preprocess(inputFilePath):
        """
        Preprocess given input file

        @param inputFilePath Path to the input dockerfile
        """

        result = ""

        # Dockerfile directory
        dir = os.path.dirname(inputFilePath)

        # Sanity check
        if not os.path.isfile(inputFilePath):
            raise RuntimeError(
                "Could not find input file: %r" % os.path.abspath(inputFilePath)
            )

        with open(inputFilePath, "r") as fileObj:
            # Go trough all the lines
            for line in fileObj.readlines():

                # Handle includes
                if line.startswith("%include="):
                    includePath = os.path.join(dir, line.split("=")[1].rstrip())

                    result += ("#" * 80) + "\n"
                    result += "# INCLUDE BEGIN %r\n#\n" % includePath

                    result += Preprocessor.preprocess(includePath)

                    result += "#\n# INCLUDE END %r\n" % includePath
                    result += ("#" * 80) + "\n"

                else:
                    result += line

        return result
