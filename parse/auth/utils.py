from parse.utils import parse

def request_password_reset(email):
    res = parse("POST", "requestPasswordReset", {
            "email":email
        })
    # success if res is {}
    return len(res) == 0
