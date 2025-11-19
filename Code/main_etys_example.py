#!/usr/bin/env python3
"""
ETYS Process Orchestration Example for main.py
Demonstrates how to integrate ETYS data processing with the Jesse PowerFactory Framework
"""

#python imports
import os, sys
import time
from pathlib import Path

# Ensure the parent directory is in the system path to import modules correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Framework"))

#framework imports
from Code import FrameworkInitialiser as f_init
from Code import GlobalEngineRegistry as gbl
from Code.NetworkDataManager import NetworkDataManager


def etys_data_processing_workflow():
    """
    Complete ETYS data processing workflow
    """
    print("🚀 Starting ETYS Data Processing Workflow")
    print("=" * 60)

    # Initialize the framework
    fw = f_init.FrameworkInitialiser()
    fw.initializeproduct(webinterfaceonly=True)
    gbl.Msg.DisplayWelcomeMessage()

    # Initialize NetworkDataManager
    print("\n📊 Initializing Network Data Manager...")
    network_manager = NetworkDataManager()

    # Display available data sources
    available_sources = network_manager.get_available_data_sources()
    print(f"✅ Available data sources: {available_sources}")

    # Example ETYS file path (adjust this to your actual file path)
    etys_file_path = r"C:\Users\solomonj\Documents\Personal\PDev\ProgrammingProjects\Jesse_PowerFactory_Modelling\Code\DataSources\Full_Grid.xlsx"

    # Check if example file exists, if not create a mock validation
    if not Path(etys_file_path).exists():
        print(f"⚠️  ETYS file not found at {etys_file_path}")
        print("📝 Creating mock validation example...")

        # Mock validation without file
        etys_reader = network_manager.get_data_reader('etys')
        etys_validator = network_manager.get_data_validator('etys')

        print(f"✅ ETYS Reader: {type(etys_reader).__name__}")
        print(f"✅ ETYS Validator: {type(etys_validator).__name__}")

        # You can test validation rules without a real file
        print("\n🧪 Testing ETYS Validation Rules...")
        # This would normally validate actual data from the Excel file

    else:
        print(f"\n📂 Processing ETYS file: {etys_file_path}")

        # Validate the ETYS file
        print("🔍 Validating ETYS data...")
        validation_result = network_manager.validate_data_source('etys', file_path=etys_file_path)

        if validation_result.is_valid():
            print("✅ ETYS data validation passed!")

            # Load the validated data
            print("\n📥 Loading ETYS data...")
            etys_data = network_manager.load_data('etys', file_path=etys_file_path)

            if etys_data:
                print("✅ ETYS data loaded successfully!")

                # Display data summary
                if 'busbars' in etys_data:
                    print(f"   • Busbars loaded: {len(etys_data['busbars'])}")
                if 'lines' in etys_data:
                    print(f"   • Lines loaded: {len(etys_data['lines'])}")
                if 'transformers' in etys_data:
                    print(f"   • Transformers loaded: {len(etys_data['transformers'])}")
                if 'generators' in etys_data:
                    print(f"   • Generators loaded: {len(etys_data['generators'])}")
                if 'loads' in etys_data:
                    print(f"   • Loads loaded: {len(etys_data['loads'])}")

                return etys_data
            else:
                print("❌ Failed to load ETYS data")
                return None
        else:
            print("❌ ETYS data validation failed!")
            print("Validation issues:")
            for msg in validation_result.messages:
                print(f"   • {msg.severity.name}: {msg.message}")
            return None


def etys_to_powerfactory_workflow(etys_data=None):
    """
    Workflow to transfer ETYS data to PowerFactory and run analysis
    """
    if not etys_data:
        print("⚠️  No ETYS data available for PowerFactory integration")
        return

    print("\n🔧 Initializing PowerFactory Backend...")
    fw = f_init.FrameworkInitialiser()

    if gbl.StudySettingsContainer.powerfactory:
        # Initialize PowerFactory backend
        fw.initialize_backend("powerfactory")

        print("✅ PowerFactory backend initialized")

        # Open or create a PowerFactory project
        print("\n📁 Setting up PowerFactory project...")
        try:
            # You can either open an existing project or create a new one
            gbl.EngineContainer.opennetwork(projectname="ETYS_Network_Model",
                                            studycasename="Base_Case")
            print("✅ PowerFactory project opened")
        except Exception as e:
            print(f"⚠️  Could not open existing project: {e}")
            print("🔧 You may need to create a new project first")

        # Here you would integrate the ETYS data with PowerFactory
        print("\n🔄 Integrating ETYS data with PowerFactory...")

        # Example integration steps (you'll need to implement these):
        # 1. Create PowerFactory elements from ETYS data
        # 2. Set electrical parameters
        # 3. Update the data model manager

        print("📝 Integration steps to implement:")
        print("   1. Create busbars in PowerFactory from ETYS busbar data")
        print("   2. Create lines with ETYS electrical parameters")
        print("   3. Create transformers with ETYS ratings")
        print("   4. Create generators with ETYS capacity data")
        print("   5. Create loads with ETYS demand data")

        # Update data model manager with network elements
        try:
            gbl.DataModelInterfaceContainer.passelementsfromnetworktodatamodelmanager()
            print("✅ Data model manager updated")

            # Run load flow analysis
            if gbl.StudySettingsContainer.DoLoadFlow:
                print("\n⚡ Running PowerFactory load flow...")
                gbl.EngineLoadFlowContainer.runloadflow()

                # Get results
                gbl.EngineLoadFlowContainer.getandupdatebusbarloadflowresults()
                gbl.EngineLoadFlowContainer.getandupdatelineloadflowresults()
                gbl.EngineLoadFlowContainer.getandupdatetransformerflowresults()
                gbl.EngineLoadFlowContainer.getandupdateloadflowgeneratorresults()
                gbl.EngineLoadFlowContainer.getandupdateloadsloadflowresults()

                print("✅ PowerFactory load flow completed successfully!")

        except Exception as e:
            print(f"⚠️  Error during PowerFactory operations: {e}")
    else:
        print("❌ PowerFactory not available in current configuration")


def main_etys_orchestration():
    """
    Main function orchestrating complete ETYS to PowerFactory workflow
    """
    try:
        # Step 1: Process ETYS data
        etys_data = etys_data_processing_workflow()

        # Step 2: Integrate with PowerFactory (if data available)
        if etys_data:
            etys_to_powerfactory_workflow(etys_data)

        print("\n🎉 ETYS orchestration workflow completed!")

    except Exception as e:
        print(f"\n❌ Error in ETYS orchestration: {e}")
        import traceback
        traceback.print_exc()


def quick_etys_test():
    """
    Quick test of ETYS data management capabilities
    """
    print("🧪 Quick ETYS Test")
    print("=" * 40)

    try:
        # Test NetworkDataManager instantiation
        network_manager = NetworkDataManager()
        print("✅ NetworkDataManager created")

        # Test data source registration
        sources = network_manager.get_available_data_sources()
        print(f"✅ Data sources available: {sources}")

        # Test reader/validator retrieval
        etys_reader = network_manager.get_data_reader('etys')
        etys_validator = network_manager.get_data_validator('etys')
        print(f"✅ ETYS Reader: {type(etys_reader).__name__}")
        print(f"✅ ETYS Validator: {type(etys_validator).__name__}")

        print("\n✅ All ETYS components working correctly!")

    except Exception as e:
        print(f"❌ ETYS test failed: {e}")
        import traceback
        traceback.print_exc()


#main driver function to initialize the framework and perform ETYS tests
if __name__ == "__main__":
    print("Jesse PowerFactory Modelling Framework - ETYS Integration")
    print("=" * 80)

    # Choose your workflow:

    # # Option 1: Quick test of ETYS components
    # print("\n1️⃣  Running quick ETYS component test...")
    # quick_etys_test()

    #Option 2: Full ETYS processing workflow (uncomment to use)
    print("\n2️⃣  Running full ETYS processing workflow...")
    main_etys_orchestration()

    # Option 3: Keep web interface running (uncomment to use)
    # print("\n🌐 Starting web interface...")
    # fw = f_init.FrameworkInitialiser()
    # fw.initializeproduct(webinterfaceonly=True)
    # print("Web interface running at http://localhost:5000")
    # print("Press Control+C to exit.")
    # try:
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     print("\nShutting down...")
