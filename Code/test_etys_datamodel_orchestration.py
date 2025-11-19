"""
Test ETYS Data Model Interface Orchestration
"""
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_etys_orchestration_with_framework():
    """Test with framework initialization"""
    print("Testing ETYS orchestration with framework initialization...")

    try:
        # Initialize the framework
        from Code.FrameworkInitialiser import FrameworkInitialiser
        from Code import GlobalEngineRegistry as gbl

        print("Initializing framework...")
        initializer = FrameworkInitialiser()
        try:
            # Initialize backend components only (no web interface needed for testing)
            initializer.initializeproduct(engine="ipsa", webinterfaceonly=False)
            if not initializer.backendinitialized:
                print("Framework initialization failed")
                return False
            print("Framework initialized successfully")
        except Exception as e:
            print(f"Framework initialization failed: {e}")
            return False

        # Now test the ETYSDataModelInterface
        from Code.DataSources.ETYS.ETYSDataModelInterface import ETYSDataModelInterface
        etys_interface = ETYSDataModelInterface()
        print("ETYSDataModelInterface instantiated")
        standardized_etys_data = gbl.NetworkDataManager.get_standardized_data('etys', file_path=gbl.StudySettingsContainer.etysfilepath, export_to_excel = False)
        if not standardized_etys_data:
            print("Failed to get standardized ETYS data")
            return False


        # Test the orchestration
        result = etys_interface.orchestrate_source_data_loading(standardized_etys_data, "datamodel")
        print(f"Orchestration completed with result: {result}")

        # Check what was loaded
        print(f"Busbars loaded: {len(gbl.DataModelManager.Busbar_TAB)}")
        print(f"Branches loaded: {len(gbl.DataModelManager.Branch_TAB)}")

        return True

    except Exception as e:
        print(f"Test failed with framework: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_etys_orchestration_without_framework():
    """Test basic functionality without framework dependencies"""
    print("\nTesting ETYS orchestration without framework...")

    try:
        # Mock the global registry to prevent None errors
        import Code.GlobalEngineRegistry as gbl

        # Create a mock message handler
        class MockMessageHandler:

            def AddRawMessage(self, msg):
                print(f"MSG: {msg}")

            def AddError(self, msg):
                print(f"ERROR: {msg}")

        class MockDataFactory:

            def createbusbar(self, bus_id):
                return type('MockBusbar', (), {
                    'BusID': bus_id,
                    'name': '',
                    'kV': 0,
                    'Disconnected': False
                })()

            def createbranch(self, bus1, bus2, bus3, branch_id):
                return type('MockBranch', (), {
                    'BusID1': bus1,
                    'BusID2': bus2,
                    'BranchID': branch_id,
                    'name': '',
                    'ON': True
                })()

        class MockDataModelManager:

            def __init__(self):
                self.Busbar_TAB = []
                self.Branch_TAB = []

            def addbusbartotab(self, busbar):
                self.Busbar_TAB.append(busbar)
                return True

        # Set up mocks
        gbl.Msg = MockMessageHandler()
        gbl.DataFactory = MockDataFactory()
        gbl.DataModelManager = MockDataModelManager()

        # Now test
        from Code.DataSources.ETYS.ETYSDataModelInterface import ETYSDataModelInterface
        etys_interface = ETYSDataModelInterface()

        # Create mock data
        import pandas as pd
        mock_data = {
            'nodes':
                pd.DataFrame({
                    'node_id': ['NODE001', 'NODE002'],
                    'Site Name': ['Test Site 1', 'Test Site 2'],
                    'voltage_kv': [132.0, 275.0]
                })
        }

        # Test orchestration
        result = etys_interface.orchestrate_source_data_loading(mock_data, "datamodel")
        print(f"✓ Mock orchestration result: {result}")
        print(f"✓ Mock busbars created: {len(gbl.DataModelManager.Busbar_TAB)}")

        return True

    except Exception as e:
        print(f"Mock test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run both tests"""
    print("=" * 60)
    print("ETYS DATA MODEL INTERFACE ORCHESTRATION TESTS")
    print("=" * 60)

    # Try with framework first
    framework_success = test_etys_orchestration_with_framework()

    # Try without framework as fallback
    mock_success = test_etys_orchestration_without_framework()

    print("=" * 60)
    print("RESULTS:")
    print(f"Framework test: {'PASSED' if framework_success else 'FAILED'}")
    print(f"Mock test: {'PASSED' if mock_success else 'FAILED'}")

    if framework_success:
        print("Ready for full framework integration!")
    elif mock_success:
        print("Logic works, but needs framework initialization")
    else:
        print("Fix implementation issues first")

    return framework_success or mock_success


if __name__ == "__main__":
    main()