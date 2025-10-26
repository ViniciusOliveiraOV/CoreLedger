import sys
import os

# Ensure project root and src/ are on sys.path so tests can import local packages
ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')

for p in (ROOT, SRC):
    if p and p not in sys.path:
        sys.path.insert(0, p)

# Optional: print for debugging when running tests
# print('PYTHONPATH adjusted:', sys.path[:3])
