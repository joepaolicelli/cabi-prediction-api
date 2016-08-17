import base64
import falcon
import logging
import os

logger = logging.getLogger("cabi_api")


def authorized(req, resp, _1):
    logger.info("Checking if request is authorized.")
    auth_header = req.get_header("Authorization")

    if not auth_header:
        logger.info("No auth header.")
        raise falcon.HTTPUnauthorized(
            "Authentication Required", "Authentication Required",
            ["cabi_predict_api"])

    # Remove auth type from header string.
    _, auth_header = auth_header.split(" ")

    plaintext = base64.b64decode(auth_header).decode('UTF-8')
    req_user, req_pass = plaintext.split(":")

    if (req_user == os.environ["API_USER"] and
            req_pass == os.environ["API_PASS"]):
        logger.info("Credentials valid, request authorized.")
        return True

    logger.info("Credentials invalid.")
    raise falcon.HTTPUnauthorized(
        "Authentication Incorrect", "Authentication Incorrect",
        ["cabi_predict_api"])
