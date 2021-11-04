# eli fessler dedicated tkgling
# clovervidia
from builtins import input
import requests
import urllib
import json
import time
from datetime import datetime

session = requests.Session()


def _get_access_token(session_token, version):
    try:
        url = "https://accounts.nintendo.com/connect/1.0.0/api/token"
        parameters = {
            "client_id":        "71b963c1b7b6d119",
            "grant_type":       "urn:ietf:params:oauth:grant-type:jwt-bearer-session-token",
            "session_token":    session_token
        }
        header = {
            "Host":            "accounts.nintendo.com",
            "User-Agent":      f"Salmonia/{version} @tkgling",
            "Accept":          "application/json",
            "Content-Length":  str(len(urllib.parse.urlencode(parameters))),
        }

        response = requests.post(url, headers=header, json=parameters)
        return json.loads(response.text)["access_token"]
    except:
        raise ValueError("The provided session_token is invalid")


def _get_splatoon_token(access_token, version):
    try:
        url = "https://api-lp1.znc.srv.nintendo.net/v1/Account/Login"
        result = _call_flapg_api(access_token, version)
        parameter = {
            "parameter": {
                "f":            result["f"],
                "naIdToken":    result["p1"],
                "timestamp":    result["p2"],
                "requestId":    result["p3"],
                "naCountry":    "JP",
                "naBirthday":   "1990-01-01",
                "language":     "ja-JP"
            }
        }
        header = {
            "Host": "api-lp1.znc.srv.nintendo.net",
            "User-Agent":       f"Salmonia/{version} @tkgling",
            "Authorization":    "Bearer",
            "X-ProductVersion": f"{version}",
            "X-Platform":       "Android",
        }

        response = requests.post(url, headers=header, json=parameter)
        return json.loads(response.text)["result"]["webApiServerCredential"]["accessToken"]
    except KeyError:
        raise ValueError(f"X-Product Version {version} is no longer available")


def _call_s2s_api(access_token, timestamp, version):
    try:
        url = "https://elifessler.com/s2s/api/gen2"
        parameters = {
            "naIdToken":    access_token,
            "timestamp":    timestamp
        }
        header = {
            "User-Agent":   f"Salmonia/{version} @tkgling",
        }

        response = requests.post(url, headers=header, data=parameters)
        if response.status_code != 200:
            raise ValueError("Too many requets")
        return json.loads(response.text)["hash"]
    except:
        raise ValueError("Too many requets")


def _call_flapg_api(access_token, version, type=True):
    try:
        url = "https://flapg.com/ika2/api/login?public"
        timestamp = int(time.time())

        header = {
            "x-token":  access_token,
            "x-time": str(timestamp),
            "x-guid": "037239ef-1914-43dc-815d-178aae7d8934",
            "x-hash": _call_s2s_api(access_token, timestamp, version),
            "x-ver": "3",
            "x-iid": "nso" if type == True else "app"
        }

        response = requests.get(url, headers=header)
        return json.loads(response.text)["result"]
    except:
        raise ValueError("Upgrade required")


def _get_splatoon_access_token(splatoon_token, version):
    try:
        url = "https://api-lp1.znc.srv.nintendo.net/v2/Game/GetWebServiceToken"
        result = _call_flapg_api(splatoon_token, version, False)
        parameter = {
            "parameter": {
                "id":                   5741031244955648,
                "f":                    result["f"],
                "registrationToken":    result["p1"],
                "timestamp":            result["p2"],
                "requestId":            result["p3"],
            }
        }
        header = {
            "Host":             "api-lp1.znc.srv.nintendo.net",
            "User-Agent":       f"Salmonia/{version} @tkgling",
            "Authorization":    f"Bearer {splatoon_token}",
            "X-ProductVersion": f"{version}",
            "X-Platform":       "Android",
        }

        response = requests.post(url, headers=header, json=parameter)
        return json.loads(response.text)["result"]["accessToken"]
    except:
        raise ValueError(f"X-Product Version {version} is no longer available")


def _get_iksm_session(splatoon_access_token):
    url = "https://app.splatoon2.nintendo.net"
    header = {
        "Cookie": "iksm_session=",
        "X-GameWebToken":   splatoon_access_token
    }

    response = requests.get(url, headers=header)
    return response.cookies["iksm_session"]


def get_cookie(session_token, version):
    print(f'{datetime.now().strftime("%H:%M:%S")} アクセストークンを取得しています')
    access_token = _get_access_token(session_token, version)
    print(f'{datetime.now().strftime("%H:%M:%S")} スプラトゥーントークンを取得しています')
    splatoon_token = _get_splatoon_token(access_token, version)
    print(f'{datetime.now().strftime("%H:%M:%S")} アクセストークンを取得しています')
    splatoon_access_token = _get_splatoon_access_token(splatoon_token, version)
    print(f'{datetime.now().strftime("%H:%M:%S")} 認証情報を取得しています')
    iksm_session = _get_iksm_session(splatoon_access_token)

    return iksm_session


def _check_iksm_session_validation(iksm_session):
    url = "https://app.splatoon2.nintendo.net/api/coop_results"
    headers = {
        "cookie": f"iksm_session={iksm_session}"
    }
    if requests.get(url, headers=headers).status_code == 200:
        return True


def _get_coop_summary(iksm_session):
    url = "https://app.splatoon2.nintendo.net/api/coop_results"
    headers = {
        "cookie": f"iksm_session={iksm_session}"
    }
    return requests.get(url, headers=headers).json()
