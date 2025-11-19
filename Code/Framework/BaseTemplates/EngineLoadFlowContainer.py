from Code import GlobalEngineRegistry as gbl

class EngineLoadFlowContainer:
    def __init__(self):
        pass

    #__________________________ENGINE LOAD FLOW METHODS________________________
    def runloadflow(self):
        """This method runs the load flow analysis."""
        raise NotImplementedError("This method should be implemented by subclasses.")
    def getandupdatebusbarloadflowresults(self):
        """This method retrieves the busbar results from the load flow analysis."""
        raise NotImplementedError("This method should be implemented by subclasses.")
    def getandupdatelineloadflowresults(self):
        """This method retrieves the line results from the load flow analysis."""
        raise NotImplementedError("This method should be implemented by subclasses.")

    def getandupdateloadflowgeneratorresults(self):
        """This method retrieves the generator load flow results and updates the data tab."""
        raise NotImplementedError("This method should be implemented by subclasses.")
    def getandupdatetransformerflowresults(self):
        """This method retrieves the transformer load flow results."""
        raise NotImplementedError("This method should be implemented by subclasses.")
    def getallloadflowresults(self):
        """This method retrieves the results of the load flow analysis."""
        raise NotImplementedError("This method should be implemented by subclasses.")