import sys
import logging

# Important stuff
VERSION = "1.8.2" # DON'T CHANGE THIS

# Logging
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
