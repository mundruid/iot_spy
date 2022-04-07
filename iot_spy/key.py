from random import random

import hashlib


def weak_hash(secret):
    return hashlib.md5(secret)


print(weak_key("drx"))
