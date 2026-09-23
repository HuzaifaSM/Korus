import json
from os import remove, listdir, makedirs
from os.path import exists
from datetime import datetime
from uuid import uuid4
from shutil import move
from typing import List, Optional, Tuple
from .files import PATH, _encodeKorus, _decodeKorus, _savesRoot, _saveFilePath, _createBackup
from .items.equipment import Equipment

if exists('Korus'):
    ACCOUNTS_PATH = "Korus/data/accounts/"
else:
    ACCOUNTS_PATH = "data/accounts/"

STRANDED_ACCOUNT_ID = "_stranded"
"""pseudo-account ID for saves whose real account was deleted whilst they existing"""

def ensureAccountsDirectory():
    makedirs(ACCOUNTS_PATH, exist_ok=True)

def _accountFilePath(accountId: str) -> str:
    return f"{ACCOUNTS_PATH}{accountId}.korus"

def _accountTempJsonPath(accountId: str, suffix: str = "tmp") -> str:
    return f"{ACCOUNTS_PATH}{accountId}.{suffix}.json"

class Account:
    def __init__(self, accountId: str, name: str, createdAt: str = None):
        self.accountId = accountId
        self.name = name
        self.createdAt = createdAt or datetime.now().isoformat()
        self.stashedEquipment: List[Equipment] = []

    @property
    def savesDirName(self) -> str:
        """name of account's save-fil subdirectory under data/saves/"""
        return self.accountId

    def serialise(self) -> dict:
        return {
            'accountId': self.accountId,
            'name': self.name,
            'createdAt': self.createdAt,
            'stashedEquipment': [e.serialise() for e in self.stashedEquipment],
        }

    @classmethod
    def deserialise(cls, data: dict) -> 'Account':
        account = cls(data['accountId'], data.get('name', 'Account'), data.get('createdAt'))
        account.stashedEquipment = [Equipment.deserialise(e) for e in data.get('stashedEquipment', [])]
        return account

def listAccounts() -> List[Tuple[str, str]]:
    """returns [(accountId, displayName)] for all accounts on disk sorted by name"""
    ensureAccountsDirectory()
    accounts = []
    for filename in listdir(ACCOUNTS_PATH):
        if not filename.endswith('.korus'):
            continue
        accountId = filename[:-len('.korus')]
        peekJson = _accountTempJsonPath(accountId, 'peek')
        if _decodeKorus(f"{ACCOUNTS_PATH}{filename}", peekJson):
            try:
                with open(peekJson, 'r') as f:
                    data = json.load(f)
                accounts.append((accountId, data.get('name', accountId)))
            except Exception:
                accounts.append((accountId, f"{accountId} (corrupted)"))
            finally:
                if exists(peekJson):
                    remove(peekJson)
    return sorted(accounts, key=lambda a: a[1].lower())

def createAccount(name: str) -> Account:
    ensureAccountsDirectory()
    accountId = str(uuid4())
    account = Account(accountId, name)
    saveAccount(account)
    makedirs(f"{PATH}{accountId}/", exist_ok=True)
    return account

def loadAccount(accountId: str) -> Optional[Account]:
    path = _accountFilePath(accountId)
    if not exists(path):
        return None
    tempJson = _accountTempJsonPath(accountId)
    if not _decodeKorus(path, tempJson):
        return None
    try:
        with open(tempJson, 'r') as f:
            data = json.load(f)
        return Account.deserialise(data)
    finally:
        if exists(tempJson):
            remove(tempJson)

def saveAccount(account: Account):
    ensureAccountsDirectory()
    tempJson = _accountTempJsonPath(account.accountId)
    with open(tempJson, 'w') as f:
        json.dump(account.serialise(), f, indent=4)
    _encodeKorus(tempJson, _accountFilePath(account.accountId))

def deleteAccount(accountId: str) -> bool:
    path = _accountFilePath(accountId)
    if exists(path):
        remove(path)
        return True
    return False

def strandSave(saveNum: int, fromAccountId: str) -> bool:
    sourcePath =  _saveFilePath(saveNum, fromAccountId)
    if not exists(sourcePath):
        return False
    makedirs(_savesRoot(STRANDED_ACCOUNT_ID), exist_ok=True)
    move(sourcePath, _saveFilePath(saveNum, STRANDED_ACCOUNT_ID))
    return True

def deleteAccountAndSaves(accountId: str, keepSaveNum: int = None) -> bool:
    savesDir = _savesRoot(accountId)
    if exists(savesDir):
        for filename in listdir(savesDir):
            if not (filename.startswith('Save ') and filename.endswith('.korus')):
                continue
            saveNumStr = filename.replace('Save ', '').replace('.korus', '')
            try:
                saveNumInt = int(saveNumStr)
            except ValueError:
                continue
            if keepSaveNum is not None and saveNumInt == keepSaveNum:
                continue
            _createBackup(saveNumInt, accountId)
            remove(f"{savesDir}{filename}")
    deleteAccount(accountId)

