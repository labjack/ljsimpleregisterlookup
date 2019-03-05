import collections
import copy
import unittest
import json
import os

import lj_modbus

lj_modbus.get_formatted_modbus_data()

TEST_REGISTER = """[
    [
        {
            "displayname": [
                "CIO Bit #"
            ], 
            "name": "Test#(0:3)", 
            "tags": [
                "DIO", 
                "CORE"
            ], 
            "readwrite": "RW", 
            "altnames": [
                "DIO#(16:19)"
            ], 
            "devices": [
                "T7", 
                "T4"
            ], 
            "address": 2016, 
            "type": "UINT16", 
            "description": "Read or set the state of 1 bit of digital I/O.  Also configures the direction to input or output. Read 0=Low AND 1=High. Write 0=Low AND 1=High."
        }, 
        [
            {
                "description": "Read or set the state of 1 bit of digital I/O.  Also configures the direction to input or output. Read 0=Low AND 1=High. Write 0=Low AND 1=High.", 
                "tags": [
                    "DIO", 
                    "CORE"
                ], 
                "type_index": "0", 
                "address": 2016, 
                "isBuffer": false, 
                "streamable": false, 
                "name": "CIO0", 
                "default": null, 
                "altnames": [
                    "DIO16"
                ], 
                "devices": [
                    {
                        "device": "T7", 
                        "fwmin": 0
                    }, 
                    {
                        "device": "T4", 
                        "fwmin": 0
                    }
                ], 
                "readwrite": {
                    "read": true, 
                    "write": true
                }, 
                "constants": [], 
                "type": "UINT16", 
                "usesRAM": false
            }, 
            {
                "description": "Read or set the state of 1 bit of digital I/O.  Also configures the direction to input or output. Read 0=Low AND 1=High. Write 0=Low AND 1=High.", 
                "tags": [
                    "DIO", 
                    "CORE"
                ], 
                "type_index": "0", 
                "address": 2017, 
                "isBuffer": false, 
                "streamable": false, 
                "name": "CIO1", 
                "default": null, 
                "altnames": [
                    "DIO17"
                ], 
                "devices": [
                    {
                        "device": "T7", 
                        "fwmin": 0
                    }, 
                    {
                        "device": "T4", 
                        "fwmin": 0
                    }
                ], 
                "readwrite": {
                    "read": true, 
                    "write": true
                }, 
                "constants": [], 
                "type": "UINT16", 
                "usesRAM": false
            }, 
            {
                "description": "Read or set the state of 1 bit of digital I/O.  Also configures the direction to input or output. Read 0=Low AND 1=High. Write 0=Low AND 1=High.", 
                "tags": [
                    "DIO", 
                    "CORE"
                ], 
                "type_index": "0", 
                "address": 2018, 
                "isBuffer": false, 
                "streamable": false, 
                "name": "CIO2", 
                "default": null, 
                "altnames": [
                    "DIO18"
                ], 
                "devices": [
                    {
                        "device": "T7", 
                        "fwmin": 0
                    }, 
                    {
                        "device": "T4", 
                        "fwmin": 0
                    }
                ], 
                "readwrite": {
                    "read": true, 
                    "write": true
                }, 
                "constants": [], 
                "type": "UINT16", 
                "usesRAM": false
            }, 
            {
                "description": "Read or set the state of 1 bit of digital I/O.  Also configures the direction to input or output. Read 0=Low AND 1=High. Write 0=Low AND 1=High.", 
                "tags": [
                    "DIO", 
                    "CORE"
                ], 
                "type_index": "0", 
                "address": 2019, 
                "isBuffer": false, 
                "streamable": false, 
                "name": "CIO3", 
                "default": null, 
                "altnames": [
                    "DIO19"
                ], 
                "devices": [
                    {
                        "device": "T7", 
                        "fwmin": 0
                    }, 
                    {
                        "device": "T4", 
                        "fwmin": 0
                    }
                ], 
                "readwrite": {
                    "read": true, 
                    "write": true
                }, 
                "constants": [], 
                "type": "UINT16", 
                "usesRAM": false
            }
        ]
    ]
]"""

EXPECTED_REGISTER = [{
    "displayname": [
        "CIO Bit #"
    ], 
    "name": "Test#(0:3)", 
    "tags": "<a href=\"https://labjack.com/support/datasheets/t-series/digital-io/extended-features\" target=\"_blank\">DIO</a>, CORE", 
    "readwrite": "RW", 
    "altnames": [
        "DIO#(16:19)"
    ], 
    "devices": "T7T4", 
    "list_of_names": [
        {
            "name": "CIO0", 
            "address": 2016
        }, 
        {
            "name": "CIO1", 
            "address": 2017
        }, 
        {
            "name": "CIO2", 
            "address": 2018
        }, 
        {
            "name": "CIO3", 
            "address": 2019
        }
    ], 
    "details": "<div class='expand-details'> Name: Test#(0:3)<br/>Description: Read or set the state of 1 bit of digital I/O.  Also configures the direction to input or output. Read 0=Low AND 1=High. Write 0=Low AND 1=High. <br/> <br/><table class='sub-details'><thead><tr><td>Expanded Names</td><td>Address</td></tr></thead><tbody><tr><td>CIO0, CIO1, CIO2,  <a onclick='showHidden(2016)' href='#' id='show2016' style='display: inline;'>Show All</a><span class='content-hide'  style='display: none;' id='2016'>CIO3</span></td><td>2016, 2017, 2018, <a onclick='showHidden(2016)' href='#' id='show12016' style='display: inline;'>Show All</a><span class='content-hide' style='display: none;' id='20161'>2019</span></td></tr> </tbody></table></div> ", 
    "address": 2016, 
    "type": "UINT16", 
    "description": "Read or set the state of 1 bit of digital I/O.  Also configures the direction to input or output. Read 0=Low AND 1=High. Write 0=Low AND 1=High."
}
]


TEST_REGISTER =  json.loads(TEST_REGISTER)
EXPECTED_REGISTER = json.loads(json.dumps(EXPECTED_REGISTER))
class LJModbusMapTests(unittest.TestCase):

        def test_find_error_range_from_errors_gets_all_errors(self):
            modbus_format = lj_modbus.get_formatted_modbus_data(TEST_REGISTER)
            self.assertEqual(EXPECTED_REGISTER, modbus_format)


if __name__ == "__main__":
    unittest.main()
