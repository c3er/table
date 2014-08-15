#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import collections

import table

class TestClassEntryDataInitialization(unittest.TestCase):
    def test_EntryData_initialization(self):
        io_dict = {
            None: (None, ''),
            '': (None, ''),
            'foo': (None, 'foo'),
            123: (123, ''),
            '100%': (100, '%'),
        }
        
        for arg, exp_pair in io_dict.items():
            ed = table.EntryData(arg)
            self.assertEqual(exp_pair[0], ed.number)
            self.assertEqual(exp_pair[1], ed.string)
            
    def test_EntryData_initialization_with_illegal_args(self):
        illegal_args = (object(), [], {}, )
        
        for arg in illegal_args:
            with self.assertRaises(TypeError):
                table.EntryData(arg)
                
class TestClassEntryData(unittest.TestCase):
    def setUp(self):
        self.data = (
            (2, 'r'),
            (3, 'b'),
            (2, 'b'),
        )
        self.entry_data = table.EntryData((3, 'r'))
        
    def test_equality(self):
        ed = table.EntryData((3, 'r'))
        self.assertTrue(self.entry_data == ed)
        self.assertFalse(self.entry_data != ed)
        
    def test_unequality(self):
        for d in self.data:
            ed = table.EntryData(d)
            self.assertFalse(self.entry_data == ed)
            self.assertTrue(self.entry_data != ed)
            
    def test_str(self):
        additional_data = (
            (None, ''),
            (1, ''),
            (None, 'foo'),
        )
        expected_strings = (
            '2r',
            '3b',
            '2b',
            '',
            '1',
            'foo',
        )
        data = self.data + additional_data
        for d, exp in zip(data, expected_strings):
            ed = table.EntryData(d)
            self.assertEqual(str(ed), exp)
            
    def test_setting_values(self):
        ed = table.EntryData()
        for number, string in self.data:
            ed.set(number)
            self.assertEqual(number, ed.number)
            
            ed.set(string)
            self.assertEqual(string, ed.string)
            
            ed.set((number, string))
            self.assertEqual(number, ed.number)
            self.assertEqual(string, ed.string)
            
class TestClassEntry(unittest.TestCase):
    def setUp(self):
        self.entry = table.Entry()

class TestFunctionSplitData(unittest.TestCase):
    def test_all_kinds_of_strings_and_None_as_parameter(self):
        io_dict = {
            None: (None, ''),
            '': (None, ''),
            '100': (100, ''),
            '-100': (-100, ''),
            '- 100': (-100, ''),
            '100.5': (100.5, ''),
            '-100.5': (-100.5, ''),
            '- 100.5': (-100.5, ''),
            '100%': (100, '%'),
            '-100%': (-100, '%'),
            '- 100%': (-100, '%'),
            '100.5%': (100.5, '%'),
            '-100.5%': (-100.5, '%'),
            '- 100.5%': (-100.5, '%'),
            '100.5 %': (100.5, '%'),
            '-100.5 %': (-100.5, '%'),
            '- 100.5 %': (-100.5, '%'),
            'hello': (None, 'hello'),
            'hello123': (None, 'hello123'),
        }
        
        for arg, expected in io_dict.items():
            self.assertEqual(table.split_data(arg), expected)
            
    def test_other_then_str_is_not_allowed(self):
        illegal_args = (123, 12.5, object(), ['a', 'b', 'c'])
        
        for arg in illegal_args:
            with self.assertRaises(TypeError):
                table.split_data(arg)
                
class TestFunctionIsListLike(unittest.TestCase):
    def test_list_like_objects_are_recognized(self):
        data = ([], (), collections.UserList(), table.TableRow(None))
        for listobj in data:
            self.assertTrue(table.islistlike(listobj))
            
    def test_other_objects_are_not_list_like(self):
        data = ('', {}, 1, 1.1, table.Table())
        for obj in data:
            self.assertFalse(table.islistlike(obj))

def main():
    unittest.main(verbosity = 2)

if __name__ == '__main__':
    main()
