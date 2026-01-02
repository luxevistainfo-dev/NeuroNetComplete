import os
import json
import time
import threading
import uuid
import re

NFTS_FILE = os.path.join(os.path.dirname(file), "..", "data", "nfts.json")
LOCK = threading.Lock()

# in-memory ca
