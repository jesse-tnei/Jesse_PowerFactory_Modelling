from Code import GlobalEngineRegistry as gbl

class EngineLoadFlowContainer:
    def __init__(self):
        pass

    #__________________________ENGINE LOAD FLOW METHODS________________________
    def runloadflow(self):
        """This method runs the load flow analysis."""
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def getloadflowresults(self):
        """This method retrieves the results of the load flow analysis."""
        raise NotImplementedError("This method should be implemented by subclasses.")