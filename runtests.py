import sys

import unittest

from lj_scribe_test import *
from parse_ljsl_test import *
from serialize_test import *
from lj_error_scribe_test import *

sys.path.append('./ljm_constants')
from ljmmm_test import *

if __name__ == "__main__":
    unittest.main()
