# -*- coding: utf-8 -*-

import os
import sys
import unittest

from pywebapi import ModuleImporter, util


class TestMain(unittest.TestCase):
    def setUp(self):
        self.cur_dir = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))

    def test_full_path(self):
        fp = util.full_path(None)
        self.assertEqual(fp, self.cur_dir)

        fp = util.full_path('')
        self.assertEqual(fp, self.cur_dir)

        fp = util.full_path('.')
        self.assertEqual(fp, self.cur_dir)

        np = self.cur_dir + r'\test\test_directory'
        fp = util.full_path('./test/test_directory')
        self.assertEqual(fp, np)

        fp = util.full_path('test/test_directory')
        self.assertEqual(fp, np)


    def test_same_path(self):
        tp = os.path.join(self.cur_dir, r'..\Sample\PyWebApi.IIS\user-script-root\test_directory')
        self.assertTrue(util.same_path(r'..\Sample\PyWebApi.IIS\user-script-root\test_directory', tp))
        self.assertTrue(util.same_path('../Sample/PyWebApi.IIS/user-script-root/test_directory', tp))
        self.assertTrue(util.same_path('../sample/pywebapi.iis/user-script-root/test_directory', tp))


    def test_extract_path_info(self):
        self.assertEqual(util.extract_path_info('/abc/def/ghi.func'), ('abc/def', 'ghi', 'func'))
        self.assertEqual(util.extract_path_info('/abc/def/ghi.func/'), ('abc/def', 'ghi', 'func'))
        self.assertEqual(util.extract_path_info('/abc/def/ghi.func//'), ('abc/def', 'ghi', 'func'))
        self.assertEqual(util.extract_path_info('/abc/def/func'), ('abc', 'def', 'func'))
        #self.assertEqual(util.extract_path_info('/def/func'), ('', 'def', 'func'))
        #self.assertEqual(util.extract_path_info('/ghi.func'), ('', 'ghi', 'func'))
        #self.assertEqual(util.extract_path_info('ghi.func'), ('', 'ghi', 'func'))
        #self.assertEqual(util.extract_path_info('.func'), ('', '', 'func'))
        #self.assertEqual(util.extract_path_info('./'), ('', '', ''))


    def test_invoke_overall(self):

        with ModuleImporter('../Sample/PyWebApi.IIS/user-script-root/test_directory', 'test_module') as runspace:
            d = {'': {20, 80, 120}, 'arg3': 30.28}
            a = [d, d]
            try:
                runspace.invoke('module_level_function', a)
            except Exception as e:
                t = e


if __name__ == '__main__':
    unittest.main()
