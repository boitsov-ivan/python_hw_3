import hashlib
import base64
import random

def short_url(long_url: str) -> str:
    hashed_url = hashlib.sha256(long_url.encode('utf-8')).digest()
    base64_encoded = base64.urlsafe_b64encode(hashed_url).decode('utf-8')
    short_code = base64_encoded[:8]
    return ''.join(sorted(short_code, key=lambda x: random.random()))




