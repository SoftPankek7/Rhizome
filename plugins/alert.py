import os
from urllib.parse import urlparse, parse_qs

def api(list):

    req   = list[0]   # "GET" or "POST"
    http  = list[1]   # handler instance
    params = list[2]  # query/body params

    # Safely extract parameter
    name = params.get("personName", ["Unknown"])[0]

    os.system(f"notify-send '{req} | {name}'")

    # Example logic:
    # - redirect to "/"
    # - no body output
    return {
        "redirect": "/",
        "body": None,
        "mime": None
    }


def api_init():
    os.system("notify-send 'Alert API Started!'")
