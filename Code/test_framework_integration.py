#!/usr/bin/env python3
"""
Test NetworkDataManager integration with the framework
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_framework_integration():
    """Test the complete framework integration with NetworkDataManager"""

    print("🚀 Testing Framework Integration with NetworkDataManager")
    print("=" * 60)

    try:
        # Import framework components
        from Code.FrameworkInitialiser import FrameworkInitialiser
        from Code import GlobalEngineRegistry as gbl

        print("✅ Successfully imported framework components")

        # Initialize the framework
        print("\n📦 Initializing Framework...")
        framework = FrameworkInitialiser()

        # Initialize web-only first (messaging and settings)
        success = framework.initialize_web_only()
        if not success:
            print("❌ Failed to initialize web components")
            return False

        print("✅ Web components initialized")

        # Initialize backend (including NetworkDataManager)
        print("\n🔧 Initializing Backend...")
        success = framework.initialize_backend("powerfactory")
        if not success:
            print("❌ Failed to initialize backend")
            return False

        print("✅ Backend initialized successfully")

        # Test NetworkDataManager availability
        print("\n🧪 Testing NetworkDataManager...")

        if not hasattr(gbl, 'NetworkDataManager'):
            print("❌ NetworkDataManager not found in global registry")
            return False

        network_manager = gbl.NetworkDataManager
        print(f"✅ NetworkDataManager available: {type(network_manager).__name__}")

        # Test data source registration
        print("\n📊 Testing Data Source Registration...")
        data_sources = network_manager.get_available_data_sources()
        print(f"✅ Available data sources: {data_sources}")

        if 'ETYS' not in data_sources:
            print("❌ ETYS data source not registered")
            return False

        print("✅ ETYS data source properly registered")

        # Test ETYS reader creation
        print("\n📂 Testing ETYS Reader Creation...")
        etys_reader = network_manager.get_data_reader('ETYS')
        print(f"✅ ETYS reader created: {type(etys_reader).__name__}")

        # Test framework status
        print("\n📋 Framework Status:")
        status = framework.get_framework_status()
        for key, value in status.items():
            print(f"  • {key}: {value}")

        print("\n🎉 All integration tests passed!")
        print("=" * 60)
        print("The NetworkDataManager is successfully integrated into the framework!")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        try:
            if 'framework' in locals():
                framework.cleanup()
            print("\n🧹 Framework cleaned up")
        except:
            pass


if __name__ == "__main__":
    success = test_framework_integration()
    sys.exit(0 if success else 1)
