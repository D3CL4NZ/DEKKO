import sys
import logging
import discord

# Important stuff
VERSION = "1.5.0" # DON'T CHANGE THIS

# Logging
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
