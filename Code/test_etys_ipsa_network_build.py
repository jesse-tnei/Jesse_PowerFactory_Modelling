"""
Integration Test: ETYS Excel -> DataModel -> IPSA Pipeline
Tests the complete data flow from Excel file to IPSA network creation.
"""
import sys
import os
# Ensure the parent directory is in the system path to import modules correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Framework"))


from Code import GlobalEngineRegistry as gbl
from Code.NetworkDataManager import NetworkDataManager
from Code.FrameworkInitialiser import FrameworkInitialiser

def test_complete_etys_pipeline():
    """Test complete ETYS to IPSA pipeline"""
    # Initialize framework
    fw = FrameworkInitialiser()
    fw.initializeproduct(webinterfaceonly=False)
    # Set up test parameters
    excel_file_path = gbl.StudySettingsContainer.etysfilepath # Use your ETYS Excel file
    output_ipsa_path = r"test_etys_network.i2f"
    print("=== ETYS to IPSA Pipeline Test ===")
    try:
        # Step 1: Load ETYS data to DataModel
        print("Step 1: Loading ETYS data to framework DataModel...")
        network_manager = NetworkDataManager()
        success = network_manager.load_etys_data_to_framework(
            file_path=excel_file_path,
            load_strategy="datamodel"
        )
        if not success:
            print("FAILED: Could not load ETYS data to DataModel")
            return False
        # Check DataModel has data
        print(f"DataModel loaded:")
        print(f"   - Busbars: {len(gbl.DataModelManager.Busbar_TAB)}")
        print(f"   - Branches: {len(gbl.DataModelManager.Branch_TAB)}")
        print(f"   - Loads: {len(gbl.DataModelManager.Load_TAB)}")
        print(f"   - Generators: {len(gbl.DataModelManager.Gen_TAB)}")
        # Step 2: Create IPSA engine and load from DataModel
        print("\nStep 2: Creating IPSA engine and loading from DataModel...")
        ipsa_engine = gbl.EngineContainer
        if ipsa_engine is None:
            print("FAILED: Could not get IPSA engine")
            return False
        # Load network from DataModel and save
        success = ipsa_engine.load_etys_data_and_save(output_ipsa_path) 
        if not success:
            print("FAILED: Could not create IPSA network from DataModel")
            return False
        print(f"IPSA network created and saved to: {output_ipsa_path}")
        # Step 3: Verify the IPSA file was created
        if os.path.exists(output_ipsa_path):
            file_size = os.path.getsize(output_ipsa_path)
            print(f"IPSA file verification: {file_size} bytes")
        else:
            print("FAILED: IPSA file was not created")
            return False
        # Step 4: Try to reopen the IPSA file (validation)
        print("\nStep 3: Validating IPSA file by reopening...")
        test_engine = gbl.EngineContainer
        reopen_success = test_engine.opennetwork(filepath=output_ipsa_path)
        if reopen_success:
            print("IPSA file validation successful - file can be reopened")
            test_engine.closenetwork()
        else:
            print("WARNING: IPSA file created but cannot be reopened")
        print("\nPIPELINE TEST COMPLETED SUCCESSFULLY!")
`       `````   ``        return True
    except Exception as e:
        print(f"PIPELINE TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_complete_etys_pipeline()