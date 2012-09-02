#!/usr/bin/env python
# -*- coding: utf-8 -*-

import table

def test_split_data():
    print('Function "split_data"')
    
    print(table.split_data('100'))
    print(table.split_data('-100'))
    print(table.split_data('- 100'))
    
    print(table.split_data('100.5'))
    print(table.split_data('-100.5'))
    print(table.split_data('- 100.5'))
    
    print(table.split_data('100%'))
    print(table.split_data('-100%'))
    print(table.split_data('- 100%'))
    
    print(table.split_data('100.5%'))
    print(table.split_data('-100.5%'))
    print(table.split_data('- 100.5%'))
    
    print(table.split_data('100.5 %'))
    print(table.split_data('-100.5 %'))
    print(table.split_data('- 100.5 %'))
    
    print(table.split_data('hallo'))
    print(table.split_data('hallo123'))
    
    print()

if __name__ == '__main__':
    test_split_data()
