import hashlib


def generateApiKey(seed):
    return hashlib.sha1(seed).hexdigest()