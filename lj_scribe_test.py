import collections
import unittest

import flask

import lj_scribe
import parse_ljsl

TEST_DEVICE_REGS = (
    ({'name': 'ORIG_PRE_100_POST'}, {'name': 'PRE_100_POST'}),
    ({'name': 'ORIG_PRE_100_POST'}, {'name': 'PRE_103_POST'}),
    ({'name': 'ORIG_PRE_100_POST'}, {'name': 'PRE_200_POST'}),
    ({'name': 'ORIG_PRE_100_POST'}, {'name': 'PRE_203_POST'}),
    ({'name': 'ORIG_PRE_100_POST'}, {'name': 'PRE_300_POST'}),
    ({'name': 'ORIG_PRE_100_POST'}, {'name': 'PRE_303_POST'}),
    ({'name': 'ORIG_ANOTHER_200'}, {'name': 'ANOTHER_200'}),
    ({'name': 'ORIG_ANOTHER_200'}, {'name': 'ANOTHER_203'})
)

TEST_RESOLVED_TO_UNRESOLVED_PAIRS = map(
    lambda x: lj_scribe.UnresolvedToResolvedPair(*x),
    TEST_DEVICE_REGS
)

PRE_POST_ORIG_TAG = parse_ljsl.TagComponent('PRE_', 100, 2, 3, '_POST', True)
ANOTHER_ORIG_TAG = parse_ljsl.TagComponent('ANOTHER_', 200, 2, 3, '', True)
ORIG_TAG_NO_GAP = parse_ljsl.TagComponent('YAC', 200, 2, None, '', True)
NO_LJMMM_ORIG_TAG = parse_ljsl.TagComponent('TEST', None, None, None, None,
    False)

LOREM_IPSUM = '''Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed
do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum
dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident,
sunt in culpa qui officia deserunt mollit anim id est laborum.'''

PRE_POST_GROUPING = lj_scribe.UnresolvedWithResolvedGrouping(
    resolved=[
        {
            'name': 'PRE_100_POST',
            'address': 100,
            'readwrite': {'read': True, 'write': True},
            'type': 'UINT32'
        },
        {
            'name': 'PRE_101_POST',
            'address': 103,
            'readwrite': {'read': True, 'write': True},
            'type': 'UINT32'
        },
        {
            'name': 'PRE_102_POST',
            'address': 106,
            'readwrite': {'read': True, 'write': True},
            'type': 'UINT32'
        },
        {
            'name': 'PRE_103_POST',
            'address': 109,
            'readwrite': {'read': True, 'write': True},
            'type': 'UINT32'
        }
    ],
    unresolved={
        'name': 'ORIG_PRE_100_POST',
        'address': 100,
        'readwrite': {'read': True, 'write': True},
        'type': 'UINT32',
        'description': LOREM_IPSUM,
        'default': 1
    }
)

ANOTHER_GROUPING = lj_scribe.UnresolvedWithResolvedGrouping(
    resolved=[
        {
            'name': 'ANOTHER_200',
            'address': 200,
            'readwrite': {'read': True, 'write': False},
            'type': 'FLOAT'
        },
        {
            'name': 'ANOTHER_201',
            'address': 203,
            'readwrite': {'read': True, 'write': False},
            'type': 'FLOAT'
        }
    ],
    unresolved={
        'name': 'ORIG_ANOTHER_200',
        'address': 200,
        'readwrite': {'read': True, 'write': False},
        'type': 'FLOAT',
        'description': 'Test description 2.',
        'default': 2
    }
)

NO_LJMMM_GROUPING = lj_scribe.UnresolvedWithResolvedGrouping(
    resolved=[
        {
            'name': 'TEST',
            'address': 300,
            'readwrite': {'read': True, 'write': False},
            'type': 'FLOAT'
        }
    ],
    unresolved={
        'name': 'TEST',
        'address': 300,
        'readwrite': {'read': True, 'write': False},
        'type': 'FLOAT',
        'description': 'Test description 3.',
        'default': 2
    }
)

TEST_TAG_BY_CLASS_NAMES = collections.OrderedDict()
TEST_TAG_BY_CLASS_NAMES['ORIG_PRE_100_POST'] = PRE_POST_GROUPING
TEST_TAG_BY_CLASS_NAMES['ORIG_ANOTHER_200'] = ANOTHER_GROUPING
TEST_TAG_BY_CLASS_NAMES['TEST'] = NO_LJMMM_GROUPING

TEST_APP = flask.Flask(__name__)


class LJMMMTests(unittest.TestCase):

    def test_parsed_sub_tag_to_names(self):
        test_tag_entry = PRE_POST_ORIG_TAG

        names = lj_scribe.parsed_sub_tag_to_names(test_tag_entry)
        self.assertEqual(len(names), 2)
        self.assertEqual(names[0], 'PRE_100_POST')
        self.assertEqual(names[1], 'PRE_103_POST')


    def test_parsed_sub_tag_to_names_no_ljmmm(self):
        names = lj_scribe.parsed_sub_tag_to_names(NO_LJMMM_ORIG_TAG)
        self.assertEqual(len(names), 1)
        self.assertEqual(names[0], 'TEST')


    def test_find_classes(self):
        test_tag_entries = (
            [
                PRE_POST_ORIG_TAG,
                ANOTHER_ORIG_TAG,
                parse_ljsl.TagComponent('PRE_', 200, 2, 3, '_POST', True)
            ],
            [
                parse_ljsl.TagComponent('PRE_', 300, 2, 3, '_POST', True)
            ]
        )

        classes = lj_scribe.find_classes(test_tag_entries, TEST_DEVICE_REGS)
        self.assertEqual(len(classes), 2)

        class_group_1 = classes[0]
        self.assertEqual(len(class_group_1), 3)

        sub_group_1 = class_group_1[0]
        sub_name_group_1 = map(lambda x: x[0]['name'], sub_group_1)
        self.assertEqual(
            sub_name_group_1,
            ['ORIG_PRE_100_POST', 'ORIG_PRE_100_POST']
        )

        sub_group_2 = class_group_1[1]
        sub_name_group_2 = map(lambda x: x[0]['name'], sub_group_2)
        self.assertEqual(
            sub_name_group_2,
            ['ORIG_ANOTHER_200', 'ORIG_ANOTHER_200']
        )

        sub_group_3 = class_group_1[2]
        sub_name_group_3 = map(lambda x: x[0]['name'], sub_group_3)
        self.assertEqual(
            sub_name_group_3,
            ['ORIG_PRE_100_POST', 'ORIG_PRE_100_POST']
        )

        class_group_2 = classes[1]
        self.assertEqual(len(class_group_2), 1)

        sub_group_4 = class_group_2[0]
        sub_name_group_4 = map(lambda x: x[0]['name'], sub_group_4)
        self.assertEqual(
            sub_name_group_4,
            ['ORIG_PRE_100_POST', 'ORIG_PRE_100_POST']
        )


    def test_find_subtags_by_class(self):
        subtags_by_class = lj_scribe.find_subtags_by_class(
            [
                TEST_RESOLVED_TO_UNRESOLVED_PAIRS[:6],
                TEST_RESOLVED_TO_UNRESOLVED_PAIRS[6:]
            ],
            TEST_DEVICE_REGS
        )

        keys = subtags_by_class.keys()
        self.assertEqual(len(keys), 2)
        self.assertIn('ORIG_PRE_100_POST', keys)
        self.assertIn('ORIG_ANOTHER_200', keys)

        orig_pre_records = subtags_by_class['ORIG_PRE_100_POST']
        self.assertEqual(
            orig_pre_records.unresolved['name'],
            'ORIG_PRE_100_POST'
        )
        self.assertEqual(len(orig_pre_records.resolved), 6)
        
        orig_pre_records_names = map(
            lambda x: x['name'],
            orig_pre_records.resolved
        )
        self.assertIn('PRE_100_POST', orig_pre_records_names)
        self.assertIn('PRE_103_POST', orig_pre_records_names)
        self.assertIn('PRE_200_POST', orig_pre_records_names)
        self.assertIn('PRE_203_POST', orig_pre_records_names)
        self.assertIn('PRE_300_POST', orig_pre_records_names)
        self.assertIn('PRE_303_POST', orig_pre_records_names)

        orig_another_records = subtags_by_class['ORIG_ANOTHER_200']
        self.assertEqual(
            orig_another_records.unresolved['name'],
            'ORIG_ANOTHER_200'
        )
        self.assertEqual(len(orig_another_records.resolved), 2)

        another_records_names = map(
            lambda x: x['name'],
            orig_another_records.resolved
        )
        self.assertIn('ANOTHER_200', another_records_names)
        self.assertIn('ANOTHER_203', another_records_names)


    def test_render_tag_summary(self):
        with TEST_APP.test_request_context('/'):
            str_summary = lj_scribe.render_tag_summary(
                TEST_TAG_BY_CLASS_NAMES,
                [
                    parse_ljsl.TagComponent('PRE_', 100, 4, 3, '_POST', True),
                    ANOTHER_ORIG_TAG,
                    NO_LJMMM_ORIG_TAG
                ],
                'ORIG_TAG'
            )

        self.assertEqual(str_summary.count('class-summary'), 3)
        self.assertEqual(str_summary.count('sub-tag'), 3)
        self.assertEqual(str_summary.count('individual-name'), 7)
        self.assertEqual(str_summary.count('individual-address'), 7)
        self.assertEqual(str_summary.count('ORIG_TAG'), 1)


    def test_find_original_tag_str(self):
        tag_components = [PRE_POST_ORIG_TAG, ANOTHER_ORIG_TAG, ORIG_TAG_NO_GAP]
        original_tag_str = lj_scribe.find_original_tag_str(tag_components)
        self.assertEqual(
            original_tag_str,
            '@registers:PRE_#(100:2:3)_POST,ANOTHER_#(200:2:3),YAC#(200:2)'
        )

    def test_find_original_tag_str_no_ljmmm(self):
        tag_components = [NO_LJMMM_ORIG_TAG, PRE_POST_ORIG_TAG]
        original_tag_str = lj_scribe.find_original_tag_str(tag_components)
        self.assertEqual(
            original_tag_str,
            '@registers:TEST,PRE_#(100:2:3)_POST'
        )

if __name__ == '__main__':
    unittest.main()
