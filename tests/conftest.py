import sys
import os

# Add project src directory to sys.path for test imports
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
)
