from Code import GlobalEngineRegistry as gbl


class EngineShortCircuitContainer:
    def __init__(self):
        self.msg = gbl.Msg

    #__________________________ENGINE SHORT CIRCUIT METHODS________________________
    def runshortcircuitanalysisforallbusbars(self):
        """This method runs the short circuit analysis."""
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def getandupdateshortcircuitresults(self):
        """This method retrieves the short circuit results and updates the data tab."""
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def getallshortcircuitresults(self):
        """This method retrieves all results of the short circuit analysis."""
        raise NotImplementedError("This method should be implemented by subclasses.")