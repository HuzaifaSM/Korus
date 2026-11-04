import json
from os.path import exists

if exists('Korus'):
    SETTINGS_PATH = "Korus/settings/settings.json"
else:
    SETTINGS_PATH = "settings.json"

def loadSettings() -> dict:
    if not exists(SETTINGS_PATH):
        return {}
    try:
        with open(SETTINGS_PATH, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def saveSettings(settings: dict):
    with open(SETTINGS_PATH, 'w') as f:
        json.dump(settings, f, indent=4)

def setLastUsedAccountId(accountId):
    settings = loadSettings()
    settings['lastUsedAccountId'] = accountId
    saveSettings(settings)

