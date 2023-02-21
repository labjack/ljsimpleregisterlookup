import unittest

import parse_ljsl


TEST_CORPUS = '''There is some text followed by information about
@registers:TEST#(120:5:3) as well as a separate mixed entry about:

@registers:OTHERTEST#(1:3),TEST#(1:5:3),OTHERTEST#(1:3),lowertest#(1:3),l#(1:3)p
'''

TEST_CORPUS_MANY_WITH_INVALID = '''There is some text followed by information
about @registers:TEST#(120:5:3) and a mistake in @registers:TEST#(120d:5:3) but
not in @registers:OTHERTEST#(120:5:3)'''

TEST_CORPUS_INVALID = '''There is an invalid entry %s before the valid entry
@registers:VALID#(1:2:3)'''

POSTFIX_CORPUS = '''Of course
@registers:VALID#(1:2:3)AFTERWARDS,VALID#(4:5:6),VALIDAGAIN#(101:2:3)AFTERWARDS
demonstrate that some registers have postfixes as well. On the other hand,
some like @registers:VALID#(100:200:300) do not.'''

TEST_CORPUS_WITH_DEVICE = '''There is some text followed by information about
@registers[T4]:TEST#(120:5:3) as well as a separate mixed entry about:

@registers[T4,T7]:OTHERTEST#(1:3),TEST#(1:5:3),OTHERTEST#(1:3),lowertest#(1:3),l#(1:3)p
'''

TEST_EMPTY_DEVICE = '''There is some text followed by information about
@registers[]:TEST#(120:5:3) as well as a separate mixed entry about:
'''

class ExpandInjectDataFieldsTests(unittest.TestCase):

    def corpus_matches_tests(self, matches):
        self.assertEqual(len(matches), 2)

        lengths = [len(x) for x in matches]
        self.assertEqual([1, 5], lengths)

        target_match = matches[0][0]
        self.assertEqual(target_match.prefix, "TEST")
        self.assertEqual(target_match.start_num, 120)
        self.assertEqual(target_match.num_regs, 5)
        self.assertEqual(target_match.num_between_regs, 3)
        self.assertEqual(target_match.postfix, "")
        self.assertEqual(target_match.includes_ljmmm, True)

        target_match = matches[1][0]
        self.assertEqual(target_match.prefix, "OTHERTEST")
        self.assertEqual(target_match.start_num, 1)
        self.assertEqual(target_match.num_regs, 3)
        self.assertEqual(target_match.num_between_regs, None)
        self.assertEqual(target_match.postfix, "")
        self.assertEqual(target_match.includes_ljmmm, True)

        target_match = matches[1][1]
        self.assertEqual(target_match.prefix, "TEST")
        self.assertEqual(target_match.start_num, 1)
        self.assertEqual(target_match.num_regs, 5)
        self.assertEqual(target_match.num_between_regs, 3)
        self.assertEqual(target_match.postfix, "")
        self.assertEqual(target_match.includes_ljmmm, True)

        target_match = matches[1][2]
        self.assertEqual(target_match.prefix, "OTHERTEST")
        self.assertEqual(target_match.start_num, 1)
        self.assertEqual(target_match.num_regs, 3)
        self.assertEqual(target_match.num_between_regs, None)
        self.assertEqual(target_match.postfix, "")
        self.assertEqual(target_match.includes_ljmmm, True)

        target_match = matches[1][3]
        self.assertEqual(target_match.prefix, "lowertest")
        self.assertEqual(target_match.start_num, 1)
        self.assertEqual(target_match.num_regs, 3)
        self.assertEqual(target_match.num_between_regs, None)
        self.assertEqual(target_match.postfix, "")
        self.assertEqual(target_match.includes_ljmmm, True)

        target_match = matches[1][4]
        self.assertEqual(target_match.prefix, "l")
        self.assertEqual(target_match.start_num, 1)
        self.assertEqual(target_match.num_regs, 3)
        self.assertEqual(target_match.num_between_regs, None)
        self.assertEqual(target_match.postfix, "p")
        self.assertEqual(target_match.includes_ljmmm, True)

    def test_find_names(self):
        matches = parse_ljsl.find_names(TEST_CORPUS)
        self.corpus_matches_tests(matches)

    def test_find_names_and_device(self):
        matches = parse_ljsl.find_names(TEST_CORPUS_WITH_DEVICE)
        self.corpus_matches_tests(matches)
        self.assertEqual(len(matches), 2)
        self.assertEqual(len(matches[0][0].device_types), 1)
        self.assertEqual(    matches[0][0].device_types[0], 'T4')

        self.assertEqual(len(matches[1][0].device_types), 2)
        self.assertEqual(    matches[1][0].device_types[0], 'T4')
        self.assertEqual(    matches[1][0].device_types[1], 'T7')

        self.assertEqual(len(matches[1][1].device_types), 2)
        self.assertEqual(    matches[1][1].device_types[0], 'T4')
        self.assertEqual(    matches[1][1].device_types[1], 'T7')

        self.assertEqual(len(matches[1][2].device_types), 2)
        self.assertEqual(    matches[1][2].device_types[0], 'T4')
        self.assertEqual(    matches[1][2].device_types[1], 'T7')

        self.assertEqual(len(matches[1][3].device_types), 2)
        self.assertEqual(    matches[1][3].device_types[0], 'T4')
        self.assertEqual(    matches[1][3].device_types[1], 'T7')

        self.assertEqual(len(matches[1][4].device_types), 2)
        self.assertEqual(    matches[1][4].device_types[0], 'T4')
        self.assertEqual(    matches[1][4].device_types[1], 'T7')


    def test_empty_device_type(self):
        matches = parse_ljsl.find_names(TEST_EMPTY_DEVICE)

        self.assertEqual(len(matches), 1)
        target_match = matches[0][0]
        self.assertEqual(target_match.prefix, "TEST")
        self.assertEqual(target_match.start_num, 120)
        self.assertEqual(target_match.num_regs, 5)
        self.assertEqual(target_match.num_between_regs, 3)
        self.assertEqual(target_match.postfix, "")
        self.assertEqual(target_match.includes_ljmmm, True)
        self.assertEqual(len(matches[0][0].device_types), 0)


    def test_find_name_after_invalid(self):
        matches = parse_ljsl.find_names(
            TEST_CORPUS_MANY_WITH_INVALID)

        self.assertEqual(len(matches), 2)
        target_match = matches[0][0]
        self.assertEqual(target_match.prefix, "TEST")

        self.assertEqual(len(matches), 2)
        target_match = matches[1][0]
        self.assertEqual(target_match.prefix, "OTHERTEST")

    def test_wrong_prefix(self):
        test_corpus = TEST_CORPUS_INVALID % "@results:INVALID#(0:1)"
        matches = parse_ljsl.find_names(test_corpus)

        self.assertEqual(len(matches), 1)
        target_match = matches[0][0]
        self.assertEqual(target_match.prefix, "VALID")

    def test_missing_colon(self):
        test_corpus = TEST_CORPUS_INVALID % "@registersINVALID#(0:1)"
        matches = parse_ljsl.find_names(test_corpus)

        self.assertEqual(len(matches), 1)
        target_match = matches[0][0]
        self.assertEqual(target_match.prefix, "VALID")

    def test_missing_pound(self):
        test_corpus = TEST_CORPUS_INVALID % "@registers:NOPOUND(0:1)"
        matches = parse_ljsl.find_names(test_corpus)

        self.assertEqual(len(matches), 2)
        
        target_match = matches[0]
        self.assertEqual(len(target_match), 1)
        self.assertEqual(target_match[0].prefix, "NOPOUND")

        target_match = matches[1]
        self.assertEqual(len(target_match), 1)
        self.assertEqual(target_match[0].prefix, "VALID")

    def test_missing_front_paren(self):
        test_corpus = TEST_CORPUS_INVALID % "@registers:INVALID#0:1)"
        matches = parse_ljsl.find_names(test_corpus)

        self.assertEqual(len(matches), 1)
        target_match = matches[0][0]
        self.assertEqual(target_match.prefix, "VALID")

    def test_missing_back_paren(self):
        test_corpus = TEST_CORPUS_INVALID % "@registers:INVALID#(0:1"
        matches = parse_ljsl.find_names(test_corpus)

        self.assertEqual(len(matches), 1)
        target_match = matches[0][0]
        self.assertEqual(target_match.prefix, "VALID")

    def test_missing_param(self):
        test_corpus = TEST_CORPUS_INVALID % "@registers:INVALID#(0)"
        matches = parse_ljsl.find_names(test_corpus)

        self.assertEqual(len(matches), 1)
        target_match = matches[0][0]
        self.assertEqual(target_match.prefix, "VALID")

    def test_missing_param_value(self):
        test_corpus = TEST_CORPUS_INVALID % "@registers:INVALID#(0:)"
        matches = parse_ljsl.find_names(test_corpus)

        self.assertEqual(len(matches), 1)
        target_match = matches[0][0]
        self.assertEqual(target_match.prefix, "VALID")

    def test_missing_optional_param_value(self):
        test_corpus = TEST_CORPUS_INVALID % "@registers:INVALID#(0:1:)"
        matches = parse_ljsl.find_names(test_corpus)

        self.assertEqual(len(matches), 1)
        target_match = matches[0][0]
        self.assertEqual(target_match.prefix, "VALID")

    def test_postfix_values(self):
        matches = parse_ljsl.find_names(POSTFIX_CORPUS)

        self.assertEqual(len(matches), 2)
        self.assertEqual(len(matches[0]), 3)
        self.assertEqual(len(matches[1]), 1)
        
        target_match = matches[0][0]
        self.assertEqual(target_match.prefix, "VALID")
        self.assertEqual(target_match.start_num, 1)
        self.assertEqual(target_match.num_regs, 2)
        self.assertEqual(target_match.num_between_regs, 3)
        self.assertEqual(target_match.postfix, "AFTERWARDS")
        self.assertEqual(target_match.includes_ljmmm, True)

        target_match = matches[0][1]
        self.assertEqual(target_match.prefix, "VALID")
        self.assertEqual(target_match.start_num, 4)
        self.assertEqual(target_match.num_regs, 5)
        self.assertEqual(target_match.num_between_regs, 6)
        self.assertEqual(target_match.postfix, "")
        self.assertEqual(target_match.includes_ljmmm, True)

        target_match = matches[0][2]
        self.assertEqual(target_match.prefix, "VALIDAGAIN")
        self.assertEqual(target_match.start_num, 101)
        self.assertEqual(target_match.num_regs, 2)
        self.assertEqual(target_match.num_between_regs, 3)
        self.assertEqual(target_match.postfix, "AFTERWARDS")
        self.assertEqual(target_match.includes_ljmmm, True)

        target_match = matches[1][0]
        self.assertEqual(target_match.prefix, "VALID")
        self.assertEqual(target_match.start_num, 100)
        self.assertEqual(target_match.num_regs, 200)
        self.assertEqual(target_match.num_between_regs, 300)
        self.assertEqual(target_match.postfix, "")
        self.assertEqual(target_match.includes_ljmmm, True)

    def test_find_no_ljmmm_tag(self):
        matches = parse_ljsl.find_names("@registers:TEST")

        self.assertEqual(len(matches), 1)

        target_match = matches[0]
        self.assertEqual(len(target_match), 1)
        self.assertEqual(target_match[0].prefix, "TEST")
        self.assertEqual(target_match[0].start_num, None)
        self.assertEqual(target_match[0].num_regs, None)
        self.assertEqual(target_match[0].num_between_regs, None)
        self.assertEqual(target_match[0].postfix, None)
        self.assertEqual(target_match[0].includes_ljmmm, False)

    def test_ljmmm_and_no_ljmmm_mix(self):
        matches = parse_ljsl.find_names(
            "@registers:TEST,REST#(0:1),BES0T @registers:FEST#(0:1)"
        )

        self.assertEqual(len(matches), 2)

        target_match = matches[0]
        self.assertEqual(len(target_match), 3)
        
        self.assertEqual(target_match[0].prefix, "TEST")
        self.assertEqual(target_match[0].start_num, None)
        self.assertEqual(target_match[0].num_regs, None)
        self.assertEqual(target_match[0].num_between_regs, None)
        self.assertEqual(target_match[0].postfix, None)
        self.assertEqual(target_match[0].includes_ljmmm, False)

        self.assertEqual(target_match[1].prefix, "REST")
        self.assertEqual(target_match[1].start_num, 0)
        self.assertEqual(target_match[1].num_regs, 1)
        self.assertEqual(target_match[1].num_between_regs, None)
        self.assertEqual(target_match[1].postfix, "")
        self.assertEqual(target_match[1].includes_ljmmm, True)

        self.assertEqual(target_match[2].prefix, "BES0T")
        self.assertEqual(target_match[2].start_num, None)
        self.assertEqual(target_match[2].num_regs, None)
        self.assertEqual(target_match[2].num_between_regs, None)
        self.assertEqual(target_match[2].postfix, None)
        self.assertEqual(target_match[2].includes_ljmmm, False)

        target_match = matches[1]
        self.assertEqual(len(target_match), 1)

    def test_title_field(self):
        matches = parse_ljsl.find_names(
            "@registers(Test Section):TEST,REST#(0:1) "\
            "@registers(Test Section 2):TEST,REST#(0:1) "\
            "@registers:TEST,REST#(0:1) "
        )

        self.assertEqual(len(matches), 3)

        target_match = matches[0]
        self.assertEqual(len(target_match), 2)
        self.assertEqual(target_match[0].title, "Test Section")
        self.assertEqual(target_match[0].prefix, "TEST")
        self.assertEqual(target_match[0].start_num, None)
        self.assertEqual(target_match[0].num_regs, None)
        self.assertEqual(target_match[0].num_between_regs, None)
        self.assertEqual(target_match[0].postfix, None)
        self.assertEqual(target_match[0].includes_ljmmm, False)

        self.assertEqual(target_match[1].title, "Test Section")
        self.assertEqual(target_match[1].prefix, "REST")
        self.assertEqual(target_match[1].start_num, 0)
        self.assertEqual(target_match[1].num_regs, 1)
        self.assertEqual(target_match[1].num_between_regs, None)
        self.assertEqual(target_match[1].postfix, "")
        self.assertEqual(target_match[1].includes_ljmmm, True)

        target_match = matches[1]
        self.assertEqual(len(target_match), 2)
        self.assertEqual(target_match[0].title, "Test Section 2")
        self.assertEqual(target_match[0].prefix, "TEST")
        self.assertEqual(target_match[0].start_num, None)
        self.assertEqual(target_match[0].num_regs, None)
        self.assertEqual(target_match[0].num_between_regs, None)
        self.assertEqual(target_match[0].postfix, None)
        self.assertEqual(target_match[0].includes_ljmmm, False)

        self.assertEqual(target_match[1].title, "Test Section 2")
        self.assertEqual(target_match[1].prefix, "REST")
        self.assertEqual(target_match[1].start_num, 0)
        self.assertEqual(target_match[1].num_regs, 1)
        self.assertEqual(target_match[1].num_between_regs, None)
        self.assertEqual(target_match[1].postfix, "")
        self.assertEqual(target_match[1].includes_ljmmm, True)

        target_match = matches[2]
        self.assertEqual(len(target_match), 2)
        self.assertEqual(target_match[0].title, "")
        self.assertEqual(target_match[0].prefix, "TEST")
        self.assertEqual(target_match[0].start_num, None)
        self.assertEqual(target_match[0].num_regs, None)
        self.assertEqual(target_match[0].num_between_regs, None)
        self.assertEqual(target_match[0].postfix, None)
        self.assertEqual(target_match[0].includes_ljmmm, False)

        self.assertEqual(target_match[1].title, "")
        self.assertEqual(target_match[1].prefix, "REST")
        self.assertEqual(target_match[1].start_num, 0)
        self.assertEqual(target_match[1].num_regs, 1)
        self.assertEqual(target_match[1].num_between_regs, None)
        self.assertEqual(target_match[1].postfix, "")
        self.assertEqual(target_match[1].includes_ljmmm, True)


if __name__ == "__main__":
    unittest.main()
