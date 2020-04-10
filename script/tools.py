def make_random_key(len=16):
    import random
    import string

    return ("".join(random.sample(string.ascii_lowercase + string.ascii_uppercase + string.digits, len)))


def token_test():
    import jwt

    secret = "wxsasdsadsad"
    encode = jwt.encode({"some": "payload", "wxs": "wxs", "wsadsa": "dsadas", "dsad": "dsadsadsa"}, secret,
                        algorithm="HS256")
    print(encode)
    decode = jwt.decode(encode, secret, algorithms=["HS256"])
    print(decode)


if __name__ == '__main__':
    pass
