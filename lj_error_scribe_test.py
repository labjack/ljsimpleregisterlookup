import collections
import copy
import unittest

import flask

import lj_error_scribe



EXPECTED_ERRORS = [
    {
      "error": 0,
      "string": "LJ_SUCCESS"
    },
    {
      "error": 200,
      "string": "LJME_WARNINGS_BEGIN",
      "description": "test01"
    },
    {
      "error": 399,
      "string": "LJME_WARNINGS_END",
      "description": "test02"
    },
    {
      "error": 201,
      "string": "LJME_FRAMES_OMITTED_DUE_TO_PACKET_SIZE",
      "description": "test03"
    }
]


class LJErrorScribeTests(unittest.TestCase):
    def test_sanity(self):
        self.assertTrue(True)
    
    
    def test_find_error_range_from_errors_gets_all_errors(self):
        errors = lj_error_scribe.find_error_range_from_errors(lj_error_scribe.NEG_INF,lj_error_scribe.POS_INF,EXPECTED_ERRORS)
        self.assertEqual(EXPECTED_ERRORS,errors)
   



