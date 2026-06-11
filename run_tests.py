import unittest
import sys

def run_all_tests():
    """
    Discovers and runs all tests in the 'tests' directory.
    Outputs a summary and exits with appropriate status code.
    """
    print("Starting master test suite...")
    
    # Discover tests
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir='tests', pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures:  {len(result.failures)}")
    print(f"Errors:    {len(result.errors)}")
    print(f"Skipped:   {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("Status:    SUCCESS")
        sys.exit(0)
    else:
        print("Status:    FAILED")
        sys.exit(1)

if __name__ == '__main__':
    run_all_tests()
