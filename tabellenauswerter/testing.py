#!/usr/bin/env python
# -*- coding: utf-8 -*-

'Starting script for the test suite.'

import unittest

def main():
    loader = unittest.TestLoader()
    testcases = loader.discover('tests', '*test.py')
    suite = unittest.TestSuite(testcases)
    runner = unittest.TextTestRunner(verbosity = 2)
    runner.run(suite)
    
if __name__ == '__main__':
    main()
