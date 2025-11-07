"""
Test script for data sources integration
Tests the complete data source architecture without framework dependencies
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_basic_imports():
    """Test if all imports work correctly"""
    print("Testing imports...")
    try:
        from Code.DataSources.ValidationResult import ValidationResult, ValidationMessage, ValidationSeverity
        print("✓ ValidationResult imports successful")
    except Exception as e:
        print(f"✗ ValidationResult import failed: {e}")
        return False
    try:
        from Code.DataSources.BaseTemplates.BaseDataReader import BaseDataReader
        from Code.DataSources.BaseTemplates.BaseDataValidator import BaseDataValidator
        print("✓ Base class imports successful")
    except Exception as e:
        print(f"✗ Base class imports failed: {e}")
        return False
    try:
        from Code.DataSources.ETYS.ETYSDataReader import ETYSDataReader
        from Code.DataSources.ETYS.ETYSDataValidator import ETYSDataValidator
        print("✓ ETYS class imports successful")
    except Exception as e:
        print(f"✗ ETYS class imports failed: {e}")
        return False
    try:
        from Code.NetworkDataManager import NetworkDataManager
        print("✓ NetworkDataManager import successful")
    except Exception as e:
        print(f"✗ NetworkDataManager import failed: {e}")
        return False
    return True

def test_class_instantiation():
    """Test if classes can be instantiated correctly"""
    print("\nTesting class instantiation...")
    try:
        from Code.DataSources.ETYS.ETYSDataReader import ETYSDataReader
        from Code.DataSources.ETYS.ETYSDataValidator import ETYSDataValidator
        from Code.NetworkDataManager import NetworkDataManager
        # Test individual class instantiation
        reader = ETYSDataReader()
        print("✓ ETYSDataReader instantiated")
        validator = ETYSDataValidator()
        print("✓ ETYSDataValidator instantiated")
        manager = NetworkDataManager()
        print("✓ NetworkDataManager instantiated")
        # Test inheritance
        from Code.DataSources.BaseTemplates.BaseDataReader import BaseDataReader
        from Code.DataSources.BaseTemplates.BaseDataValidator import BaseDataValidator
        assert isinstance(reader, BaseDataReader), "ETYSDataReader should inherit from BaseDataReader"
        print("✓ ETYSDataReader inheritance verified")
        assert isinstance(validator, BaseDataValidator), "ETYSDataValidator should inherit from BaseDataValidator"
        print("✓ ETYSDataValidator inheritance verified")
        return True
    except Exception as e:
        print(f"✗ Class instantiation failed: {e}")
        return False

def test_abstract_methods():
    """Test if abstract methods are properly implemented"""
    print("\nTesting abstract method implementations...")
    try:
        from Code.DataSources.ETYS.ETYSDataReader import ETYSDataReader
        from Code.DataSources.ETYS.ETYSDataValidator import ETYSDataValidator
        reader = ETYSDataReader()
        validator = ETYSDataValidator()
        # Test required methods exist
        assert hasattr(reader, 'load_data'), "ETYSDataReader missing load_data method"
        assert hasattr(reader, 'get_supported_formats'), "ETYSDataReader missing get_supported_formats method"
        print("✓ ETYSDataReader has required methods")
        assert hasattr(validator, 'validate'), "ETYSDataValidator missing validate method"
        print("✓ ETYSDataValidator has required methods")
        # Test method signatures
        formats = reader.get_supported_formats()
        assert isinstance(formats, list), "get_supported_formats should return list"
        print(f"✓ Supported formats: {formats}")
        return True
    except Exception as e:
        print(f"✗ Abstract method test failed: {e}")
        return False

def test_network_data_manager():
    """Test NetworkDataManager functionality"""
    print("\nTesting NetworkDataManager functionality...")
    try:
        from Code.NetworkDataManager import NetworkDataManager
        manager = NetworkDataManager()
        # Test data sources registration
        sources = manager.get_available_data_sources()
        assert 'etys' in sources, "ETYS data source should be registered"
        print("✓ ETYS data source registered")
        print(f"  Available sources: {list(sources.keys())}")
        # Test error handling for invalid source
        try:
            manager.load_and_validate_data('invalid_source')
            print("✗ Should have raised error for invalid source")
            return False
        except ValueError as e:
            print("✓ Proper error handling for invalid source")
        return True
    except Exception as e:
        print(f"✗ NetworkDataManager test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("DATA SOURCE INTEGRATION TESTS")
    print("=" * 50)
    tests = [
        test_basic_imports,
        test_class_instantiation, 
        test_abstract_methods,
        test_network_data_manager
    ]
    passed = 0
    total = len(tests)
    for test in tests:
        if test():
            passed += 1
        print()
    print("=" * 50)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("=" * 50)
    if passed == total:
        print("🎉 All tests passed! Ready for framework integration.")
        return True
    else:
        print("❌ Some tests failed. Fix issues before proceeding.")
        return False

if __name__ == "__main__":
    main()