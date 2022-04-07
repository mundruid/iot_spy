"""This is a hash example algorithm."""
import hashlib


def weak_hash(secret):
    """Hash example.

    Args:
        secret (str): Plaintext secret.

    Returns:
        str: Hashed secret.
    """
    return hashlib.sha256(secret)


print(weak_hash("drx"))
