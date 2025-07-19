# This class provides a template for the EngineDataModelInterface.
# At the same time, we are using it to abstracise the EngineDataModelInterface just as we did with the Engine class 

import string
from Framework import GlobalRegistry as gbl


class EngineDataModelInterfaceContainer:
    def __init__(self):
        self.m_oEngine = gbl.Engine
        self.m_oMsg = gbl.Msg

    
    #__________________________ENGINE DATA MODEL INTERFACE METHODS________________________
    def passelementsfromnetworktodatamodelmanager(self):
        """This method retrieves elements from the network and passes them to the DataModelManager."""
        bOK = True
        if bOK:
            bOK = self.getbusbarsfromnetwork()
        if bOK:
            bOK = self.getbranchesfromnetwork()
        if bOK:
            bOK = self.getgeneratorsfromnetwork()
        if bOK:
            bOK = self.getloadsfromnetwork()
        return bOK
    
    def setelementsfromdatamodelmanagertonetwork(self):
        """This method retrieves elements from the DataModelManager and passes them to the network."""
        bOK = True
        if bOK:
            bOK = self.setbranchtonetwork()
        if bOK:
            bOK = self.setbusbartonetwork()
        if bOK:
            bOK = self.setgeneratortonetwork()
        if bOK:
            bOK = self.setloadtonetwork()

        return bOK
    
    
    #__________________COMPONENT-SPECIFIC METHOD TEMPLATES____________________________________#
    
    # BUSBARS
    def getbusbarsfromnetwork(self):
        """Retrieves busbars from the network."""
        raise NotImplementedError("This method should be implemented in subclasses.")
    def setbusbartonetwork(self):
        """Sets busbars to the network."""
        raise NotImplementedError("This method should be implemented in subclasses.")
    
    def getbusbarvaluesfromnetwork(self):
        """Retrieves busbar values from the network."""
        raise NotImplementedError("This method should be implemented in subclasses.")
    
    def setbusbarvaluesfromdatamodelmanagertonetwork(self):
        """Sets busbar values to the network."""
        raise NotImplementedError("This method should be implemented in subclasses.")
    
    
    
    # BRANCHES
    def getbranchesfromnetwork(self):
        """Retrieves branches from the network."""
        raise NotImplementedError("This method should be implemented in subclasses.")
    def setbranchestonetwork(self):
        """Sets branches to the network."""
        raise NotImplementedError("This method should be implemented in subclasses.")
    def getbranchvaluesfromnetwork(self):
        """Retrieves branch values from the network."""
        raise NotImplementedError("This method should be implemented in subclasses.")
    def setbranchvaluesfromdatamodelmanagertonetwork(self):
        """Sets branch values to the network."""
        raise NotImplementedError("This method should be implemented in subclasses.")
    
    
    # GENERATORS
    def getgeneratorsfromnetwork(self):
        """Retrieves generators from the network."""
        raise NotImplementedError("This method should be implemented in subclasses.")
    def setgeneratortonetwork(self):
        """Sets generators to the network."""
        raise NotImplementedError("This method should be implemented in subclasses.")
    def getgeneratorvaluesfromnetwork(self):
        """Retrieves generator values from the network."""
        raise NotImplementedError("This method should be implemented in subclasses.")
    def setgeneratorvaluesfromdatamodelmanagertonetwork(self):
        """Sets generator values to the network."""
        raise NotImplementedError("This method should be implemented in subclasses.")
    
    def getgeneratorstatusfromnetwork(self):
        """Retrieves generator status from the network."""
        raise NotImplementedError("This method should be implemented in subclasses.")
    def setgeneratorstatustonetwork(self):
        """Sets generator status to the network."""
        raise NotImplementedError("This method should be implemented in subclasses.")
    
    def addgeneratortonetwork(self, generator_datamodel_object):
        """Adds a generator to the network."""
        raise NotImplementedError("This method should be implemented in subclasses.")
    
    
    # LOADS
    def getloadsfromnetwork(self):
        """Retrieves loads from the network."""
        raise NotImplementedError("This method should be implemented in subclasses.")
    def setloadtonetwork(self):
        """Sets loads to the network."""
        raise NotImplementedError("This method should be implemented in subclasses.")
    def getloadvaluesfromnetwork(self):
        """Retrieves load values from the network."""
        raise NotImplementedError("This method should be implemented in subclasses.")
    def setloadvaluesfromdatamodelmanagertonetwork(self):
        """Sets load values to the network."""
        raise NotImplementedError("This method should be implemented in subclasses.")
    def addloadtonetwork(self, load_datamodel_object):
        """Adds a load to the network."""
        raise NotImplementedError("This method should be implemented in subclasses.")
    def getloadstatusfromnetwork(self):
        """Retrieves load status from the network."""
        raise NotImplementedError("This method should be implemented in subclasses.")
    def setloadstatustonetwork(self):
        """Sets load status to the network."""
        raise NotImplementedError("This method should be implemented in subclasses.")
    
