import os
import json
import time
import requests
import minecraft_launcher_lib.microsoft_account as mla

"""
AUTHENTICATION CONFIGURATION
"""
CLIENT_ID = "c36a9fb6-4f2a-41ff-90bd-ae7cc92031eb"
DEVICE_CODE_URL = "https://login.microsoftonline.com/consumers/oauth2/v2.0/devicecode"
TOKEN_URL = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
SCOPE = "XboxLive.signin offline_access"
ACCOUNT_FILE = "data/account.json"


"""
MICROSOFT OAUTH FLOW
"""
def request_device_code():
#Initiate Microsoft OAuth2 device code flow and retrieve verification code
    payload = {
        "client_id": CLIENT_ID,
        "scope": SCOPE
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(DEVICE_CODE_URL, data=payload, headers=headers, timeout=15)
    response.raise_for_status()
    return response.json()


def poll_device_token(device_code, interval=5, expires_in=900, stop_event=None, status_callback=None):
#Poll Microsoft OAuth2 token endpoint until user approves or code expires
    start_time = time.time()
    payload = {
        "client_id": CLIENT_ID,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "device_code": device_code
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    current_interval = interval
    while time.time() - start_time < expires_in:
        if stop_event and stop_event.is_set():
            return None

        time.sleep(current_interval)

        if stop_event and stop_event.is_set():
            return None

        try:
            response = requests.post(TOKEN_URL, data=payload, headers=headers, timeout=15)
            response_data = response.json()

            if response.status_code == 200 and "access_token" in response_data:
                return response_data

            error_type = response_data.get("error")
            if error_type == "authorization_pending":
                continue
            elif error_type == "slow_down":
                current_interval += 5
                continue
            elif error_type == "expired_token":
                raise Exception("The verification code has expired. Please try again.")
            elif error_type == "access_denied":
                raise Exception("Login was canceled on the Microsoft page.")
            else:
                error_description = response_data.get("error_description", error_type)
                raise Exception(f"Microsoft authentication error: {error_description}")
        except requests.RequestException:
            continue

    raise Exception("Authentication timed out. Please try again.")


"""
XBOX AND MINECRAFT SERVICES
"""
def complete_login_with_token(ms_access_token, ms_refresh_token, status_callback=None):
#Exchange Microsoft token for Xbox Live, XSTS, and Minecraft profile
    if status_callback:
        status_callback("Authenticating with Xbox Live...")

    xbl_response = mla.authenticate_with_xbl(ms_access_token)
    if "Token" not in xbl_response:
        raise Exception("Xbox Live authentication failed.")
    xbl_token = xbl_response["Token"]
    user_hash = xbl_response["DisplayClaims"]["xui"][0]["uhs"]

    if status_callback:
        status_callback("Requesting XSTS authorization...")

    xsts_response = mla.authenticate_with_xsts(xbl_token)
    if "Token" not in xsts_response:
        xsts_error = xsts_response.get("XErr")
        if xsts_error == 2148916233:
            raise Exception("This Microsoft account does not have an Xbox Live profile.\nPlease visit https://www.xbox.com to set up a Gamertag.")
        elif xsts_error == 2148916238:
            raise Exception("This account is a child account and must be added to a Microsoft Family.")
        raise Exception(f"Xbox XSTS authorization failed. (code: {xsts_error})")
    xsts_token = xsts_response["Token"]

    if status_callback:
        status_callback("Connecting to Minecraft Services...")

    mc_auth = mla.authenticate_with_minecraft(user_hash, xsts_token)
    if "access_token" not in mc_auth:
        raise Exception("Failed to authenticate with Minecraft Services.")
    mc_access_token = mc_auth["access_token"]

    if status_callback:
        status_callback("Fetching Minecraft profile...")

    profile = mla.get_profile(mc_access_token)
    if "error" in profile and profile.get("error") == "NOT_FOUND":
        raise Exception("This Microsoft account does not own Minecraft Java Edition.")
    if "name" not in profile or "id" not in profile:
        raise Exception("Failed to retrieve Minecraft profile details.")

    account_data = {
        "name": profile["name"],
        "id": profile["id"],
        "access_token": mc_access_token,
        "refresh_token": ms_refresh_token,
        "skins": profile.get("skins", []),
        "capes": profile.get("capes", []),
        "saved_at": time.time()
    }
    return account_data


def refresh_account_token(refresh_token, status_callback=None):
#Refresh Minecraft account credentials using the saved refresh token
    payload = {
        "client_id": CLIENT_ID,
        "scope": SCOPE,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(TOKEN_URL, data=payload, headers=headers, timeout=15)
        response_data = response.json()
    except Exception:
        response_data = {}

    if "access_token" not in response_data:
        try:
            response_data = mla.refresh_authorization_token(CLIENT_ID, None, None, refresh_token)
        except Exception:
            pass

    if "access_token" not in response_data:
        raise Exception("Session expired or invalid refresh token.")

    new_ms_access_token = response_data["access_token"]
    new_ms_refresh_token = response_data.get("refresh_token", refresh_token)

    account_data = complete_login_with_token(new_ms_access_token, new_ms_refresh_token, status_callback)
    save_account(account_data)
    return account_data


"""
ACCOUNT SESSION MANAGEMENT
"""
def save_account(account_data):
#Save account data to local JSON file
    try:
        with open(ACCOUNT_FILE, "w", encoding="utf-8") as file:
            json.dump(account_data, file, indent=4)
    except Exception as error:
        print(f"Failed to save account: {error}")


def load_account():
#Load saved account data from local JSON file
    if not os.path.exists(ACCOUNT_FILE):
        return None
    try:
        with open(ACCOUNT_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            if data and "name" in data and "id" in data and "refresh_token" in data:
                return data
    except Exception:
        return None
    return None


def remove_account():
#Delete saved account data from local JSON file
    if os.path.exists(ACCOUNT_FILE):
        try:
            os.remove(ACCOUNT_FILE)
        except Exception:
            pass
