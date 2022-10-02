from flask import Request
from app.internal.constants import IS_PROD


def prod_ip_resolver(req: Request):
    headers = req.headers
    cf = headers.get("x-real-ip") or headers.get("cf-connecting-ip")
    if cf:
        return cf
    return headers.get("x-forwarded-for", req.remote_addr).split(",")[-1].strip()


def dev_ip_resolver(req: Request):
    host = req.remote_addr
    print("[ip]", host)
    return host


ip_resolver = prod_ip_resolver if IS_PROD else dev_ip_resolver
