# Messaging.py
# This file contains the Messaging class, which is used to handle messaging within the application.

from Framework import GlobalRegistry as gbl
import datetime


class Messaging:
    nWarningCount = 0
    nErrorCount = 0
    nInfoCount = 0

    oFileMsgs = None
    oFileWarnings = None
    oFileErrors = None

    bPrintMsgsToConsole = None
    bPrintWarningsToConsole = None
    bPrintErrorsToConsole = None

    bMode = gbl.VERSION_TESTING

    def __init__(self):
        self.set_mode(self.bMode)

    def set_mode(self, bMode):
        # Close any existing files first
        self.close_log_files()

        self.bMode = bMode
        self.bPrintMsgsToConsole = bMode
        self.bPrintWarningsToConsole = bMode
        self.bPrintErrorsToConsole = bMode

        if not self.bMode:

            # Set file names for logging
            self.strFileMsgName = "messages.log"
            self.strFileWarningName = "warnings.log"
            self.strFileErrorName = "errors.log"

            # Open files for appending
            self.oFileMsgs = open(self.strFileMsgName, 'a', encoding='utf-8')
            self.oFileWarnings = open(self.strFileWarningName, 'a', encoding='utf-8')
            self.oFileErrors = open(self.strFileErrorName, 'a', encoding='utf-8')

    # __________________________CLOSE LOG FILES________________________
    def close_log_files(self):
        """Close all open log files"""
        if self.oFileMsgs:
            self.oFileMsgs.close()
            self.oFileMsgs = None
        if self.oFileWarnings:
            self.oFileWarnings.close()
            self.oFileWarnings = None
        if self.oFileErrors:
            self.oFileErrors.close()
            self.oFileErrors = None

    #_________________________INFORMATION MESSAGES________________________
    def AddInfo(self, sMsg):
        """Add an informational message to the log"""
        self.nInfoCount += 1
        try:
            sMsg = str(sMsg)
            sMsg = f"{datetime.datetime.now()} - INFO: {sMsg}"
        except (ValueError, TypeError) as e:
            sMsg = f"{datetime.datetime.now()} - Error formatting info message: {e}"
            return

        if self.bPrintMsgsToConsole:
            print(sMsg)

        if self.oFileMsgs:
            self.oFileMsgs.write("\n" + sMsg)

    #_________________________RAW MESSAGES (NO TIMESTAMP)________________________
    def AddRawMessage(self, sMsg):
        """Add a raw message without timestamp/prefix - for splash screens"""
        if self.bPrintMsgsToConsole:
            print(sMsg)

        if self.oFileMsgs:
            self.oFileMsgs.write("\n" + sMsg)

    #_________________________WARNING MESSAGES________________________
    def AddWarning(self, sMsg):
        """Add a warning message to the log"""
        self.nWarningCount += 1
        try:
            sMsg = str(sMsg)
            sMsg = f"{datetime.datetime.now()} - WARNING: {sMsg}"
        except (ValueError, TypeError) as e:
            sMsg = f"{datetime.datetime.now()} - Error formatting warning message: {e}"
            return

        if self.bPrintWarningsToConsole:
            print(sMsg)

        if self.oFileWarnings:
            self.oFileWarnings.write("\n" + sMsg)

    #_________________________ERROR MESSAGES________________________
    def AddError(self, sMsg):
        """Add an error message to the log"""
        self.nErrorCount += 1
        try:
            sMsg = str(sMsg)
            sMsg = f"{datetime.datetime.now()} - ERROR: {sMsg}"
        except (ValueError, TypeError) as e:
            sMsg = f"{datetime.datetime.now()} - Error formatting error message: {e}"
            return

        if self.bPrintErrorsToConsole:
            print(sMsg)

        if self.oFileErrors:
            self.oFileErrors.write("\n" + sMsg)

    #________________________CONVENIENT OVERRIDES________________________
    def add_information(self, sMsg):
        """Convenience method to add an informational message"""
        self.AddInfo(sMsg)

    def add_warning(self, sMsg):
        """Convenience method to add a warning message"""
        self.AddWarning(sMsg)

    def add_error(self, sMsg):
        """Convenience method to add an error message"""
        self.AddError(sMsg)

    #_________________________DESTRUCTOR________________________
    def __del__(self):
        """Destructor to ensure files are closed when object is destroyed"""
        self.close_log_files()

    #_________________________SPLASH SCREEN MESSAGE________________________

    def DisplayWelcomeMessage(self):
        import textwrap

        strFrameworkVer = gbl.gbl_sFrameworkVersion
        if (gbl.VERSION_TESTING):
            strFrameworkVer += "  (DEVELOPMENT VERSION)"
        d = datetime.datetime.now()

        # Don't override the app name - use what was set by FrameworkInitialiser
        strSplash = f"""\
        ##############################################################
        #                 Copyright (c) 2010 - {d.year}                  #
        #------------------------------------------------------------#
        # Product:     {gbl.gbl_sAppName:<44}  #"""

        # Description (if available)
        if gbl.gbl_sDescription:
            lLines = textwrap.wrap(gbl.gbl_sDescription, 44)
            if len(lLines):
                strFirstLine = lLines.pop(0)
                strSplash += f"\n# Description: {strFirstLine:<42}#"
                for strLine in lLines:
                    strSplash += f"\n#              {strLine:<42}  #"

        # Engine information
        strEngineType = ""
        bEngineError = False
        try:
            strEngineType = gbl.Engine.m_strVersion
        except:
            strEngineType = "Engine not available"
            bEngineError = False

        # Author information
        strAuthor = ""
        try:
            strAuthor = gbl.Engine.get_author()
        except:
            strAuthor = gbl.gbl_sAuthor

        # Add formatted lines
        strSplash += f"""
        # Engine:     {strEngineType:<44}   #
        # Framework:   {strFrameworkVer:<44}  #
        # Designer:    {strAuthor:<44}  #
        ##############################################################"""

        if (bEngineError):
            import sys
            self.AddError(strSplash)
            sys.exit(1)
        self.AddRawMessage(strSplash)

    def WordWrap(self, text, width):
        """
        A word-wrap function that preserves existing line breaks
        and most spaces in the text. Expects that existing line
        breaks are posix newlines (\n).
        (From: http://code.activestate.com/recipes/148061/)
        """
        from functools import reduce
        return reduce(lambda line, word, width=width: '%s%s%s' % (line, ' \n'[
            (len(line) - line.rfind('\n') - 1 + len(word.split('\n', 1)[0]) >= width)], word),
                      text.split(' '))
