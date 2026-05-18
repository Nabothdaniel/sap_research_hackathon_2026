# This file stays in the root to help pytest discover modules correctly
import os
import sys

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
