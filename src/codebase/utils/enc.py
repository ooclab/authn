import hashlib
import random
import string


def _hash(salt, raw_password):
    data = "{0}{1}".format(salt, raw_password)
    return hashlib.sha512(data.encode("UTF-8")).hexdigest()


def encrypt_password(plaintext):
    salt = "".join(random.sample(string.ascii_letters + string.digits, 32))
    hashstr = _hash(salt, plaintext)
    return f"{salt}${hashstr}"


def check_password(raw_password, enc_password):
    salt, hashstr = enc_password.split("$")
    return hashstr == _hash(salt, raw_password)
