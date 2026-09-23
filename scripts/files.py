import json
import traceback
import subprocess
from os.path import exists, isfile, join, dirname, abspath
from os import remove, listdir, makedirs
from datetime import datetime
from shutil import copy2
from .styles import console, printSuccess, printError, printInfo, pause, printHeader, clearScreen

if exists('Korus'):
    PATH        = "Korus/data/saves/"
    LOGS        = "Korus/data/logs/"
    BACKUP_PATH = "Korus/data/saves/.backup/"
    TOOLS_PATH  = "Korus/tools/"
else:
    PATH        = "data/saves/"
    LOGS        = "data/logs/"
    BACKUP_PATH = "data/saves/.backup/"
    TOOLS_PATH  = "tools/"

_HERE = dirname(abspath(__file__))
_KORUS_ROOT = dirname(_HERE)
KORUS_SAVE_EXE = join(_KORUS_ROOT, "tools", "korus_save.exe")

def _savesRoot(accountId: str = None) -> str:
    return f"{PATH}{accountId}/" if accountId else PATH

def _backupRoot(accountId: str = None) -> str:
    return f"{BACKUP_PATH}{accountId}/" if accountId else BACKUP_PATH

def ensureDirectories(accountId: str = None):
    makedirs(_savesRoot(accountId), exist_ok=True)
    makedirs(LOGS, exist_ok=True)
    makedirs(_backupRoot(accountId), exist_ok=True)
    makedirs(TOOLS_PATH, exist_ok=True)

# .korus encode/decode wrappers

def _encodeKorus(jsonPath: str, korusPath: str) -> bool:
    """Encodes a JSON file into a .korus binary. Returns True on success."""
    try:
        result = subprocess.run(
            [KORUS_SAVE_EXE, "--encode", jsonPath, korusPath],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            printError(f"Encode Failed: {result.stderr.strip()}")
            return False
        # removes temporary JSON once encoded
        if exists(jsonPath):
            remove(jsonPath)
        return True
    except FileNotFoundError:
        printError(f"korus_save.exe not found at '{KORUS_SAVE_EXE}'. Save file will remain as JSON.")
        return False
    except Exception as e:
        printError(f"Encode Error: {e}")
        return False
    
def _decodeKorus(korusPath: str, jsonPath: str) -> bool:
    """Decodes a .korus file back into JSON. Returns True on success."""
    try:
        result = subprocess.run(
            [KORUS_SAVE_EXE, "--decode", korusPath, jsonPath],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            printError(f"Decode Failed: {result.stderr.strip()}")
            return False
        return True
    except FileNotFoundError:
        printError(f"korus_save.exe not found at '{KORUS_SAVE_EXE}'.")
        return False
    except Exception as e:
        printError(f"Decode Error: {e}")
        return False

# helpers

def _saveFilePath(saveNum: int, accountId: str = None) -> str:
    return f"{_savesRoot(accountId)}Save {saveNum}.korus"

def _tempJsonPath(saveNum: int, accountId: str = None) -> str:
    """Temporary json path used during encode/decode"""
    return f"{_savesRoot(accountId)}Save {saveNum}.tmp.json"

def _backupPath(saveNum: int, accountId: str = None) -> str:
    return f"{_savesRoot(accountId)}Save {saveNum}.backup.korus"

# crash logging

def logCrash(exception: Exception, game=None):
    ensureDirectories()
    crashTime      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    crash_filename = datetime.now().strftime("%Y%m%d_%H%M%S")
    crashData = {
        "timestamp":        crashTime,
        "exception_type":   type(exception).__name__,
        "exception_message": str(exception),
        "traceback":        traceback.format_exc(),
        "game_state_saved": False
    }
    if game and hasattr(game, 'player') and game.player:
        try:
            saveData = {
                "player": game.player._serialise(),
                "camp":   game.camp._serialiseAll(),
                "game":   game._serialise()
            }
            with open(f"{LOGS}Crash Save {crash_filename}.json", 'w') as outFile:
                json.dump(saveData, outFile, indent=4)
            crashData["game_state_saved"]  = True
            crashData["crash_save_file"]   = f"{LOGS}Crash Save {crash_filename}"
            crashData["player_name"]       = game.player._name
            crashData["player_level"]      = game.player._level
            crashData["battles_won"]       = game.battlesWon
        except Exception as save_error:
            crashData["game_state_save_error"] = str(save_error)

    crash_log_path  = f"{LOGS}crash_{crash_filename}.log"
    crash_json_path = f"{LOGS}crash_{crash_filename}.json"

    with open(crash_log_path, 'w') as logFile:
        logFile.write("=" * 40 + "\n")
        logFile.write(f"CRASH REPORT - {crashTime}\n")
        logFile.write("=" * 40 + "\n")
        logFile.write(f"Exception Type: {crashData['exception_type']}\n")
        logFile.write(f"Exception Message: {crashData['exception_message']}\n\n")
        if crashData.get('player_name'):
            logFile.write(f"Player: {crashData['player_name']} (Level {crashData['player_level']})\n")
            logFile.write(f"Battles Won: {crashData['battles_won']}\n\n")
        logFile.write("Full Traceback:\n")
        logFile.write("-" * 40 + "\n")
        logFile.write(crashData['traceback'])
        logFile.write("-" * 40 + "\n\n")
        if crashData['game_state_saved']:
            logFile.write(f"Game state saved to: {crashData['crash_save_file']}\n")
        elif 'game_state_save_error' in crashData:
            logFile.write(f"Failed to save game state: {crashData['game_state_save_error']}\n")

        with open(crash_json_path, 'w') as jsonFile:
            json.dump(crashData, jsonFile, indent=4)

    return crash_log_path, crash_json_path

# backup

def _createBackup(saveNum: int, accountId: str = None) -> bool:
    savePath = _saveFilePath(saveNum, accountId)
    if exists(savePath):
        try:
            ensureDirectories(accountId)
            copy2(savePath, _backupPath(saveNum, accountId))
            return True
        except Exception as e:
            printError(f"Failed to create backup: {e}")
            return False
    return False

def undoLastOperation(accountId: str = None) -> bool:
    ensureDirectories(accountId)
    backupRoot = _backupRoot(accountId)
    backups = [f for f in listdir(backupRoot) if f.endswith('.backup.korus')]

    if not backups:
        printError("No backup available to undo.")
        pause()
        return False

    console.print("[info]Available backups to restore:[/info]")
    for backup in backups:
        saveNum = backup.split()[1].split('.')[0]
        console.print(f"  - Save {saveNum}")

    try:
        saveNum = int(console.input("\n[prompt]Enter save number to restore (or -1 to cancel): [/prompt]").strip())
        if saveNum == -1:
            printInfo("Undo cancelled.")
            pause()
            return False

        backupPath = _backupPath(saveNum, accountId)
        savePath   = _saveFilePath(saveNum, accountId)

        if not exists(backupPath):
            printError(f"No backup found for Save {saveNum}.")
            pause()
            return False

        confirm = console.input(
            f"[warning]Restore Save {saveNum} from backup? This will overwrite the current save. (y/N): [/warning]"
        ).strip().lower()

        if confirm == 'y':
            try:
                copy2(backupPath, savePath)
                remove(backupPath)
                printSuccess(f"Save {saveNum} restored from backup.")
                pause()
                return True
            except Exception as e:
                printError(f"Failed to restore backup: {e}")
                pause()
                return False
        else:
            printInfo("Restore cancelled.")
            pause()
            return False

    except ValueError:
        printError("Invalid input.")
        pause()
        return False
    
# save

def displayExistingSaves(accountId: str = None) -> list:
    from .difficulty import Difficulty
    clearScreen()
    printHeader("Existing Saves")
    saves = []
    ensureDirectories(accountId)
    savesRoot = _savesRoot(accountId)
    for filename in sorted(listdir(savesRoot)):
        if filename.startswith('Save ') and filename.endswith('.korus'):
            saveNum = filename.replace("Save ", "").replace(".korus", "")
            try:
                tempJson = f"{PATH}Save {saveNum}.temp.json"
                if not _decodeKorus(f"{PATH}{filename}", tempJson):
                    raise Exception(f"Failed to decode save {saveNum}")
                with open(tempJson, 'r') as f:
                    data: dict = json.load(f)
                remove(tempJson)
                player: dict = data.get('player', None)
                if not player:
                    raise Exception(f"Player data missing from save {saveNum}")

                playerName = player.get('name', 'The Hero')
                playerLevel = player.get('level', 1)
                className = player.get('className')

                if not className:
                    raise Exception(f"Player has no class data in save {saveNum}")
                
                game: dict = data.get('game', {})

                if not game:
                    raise Exception(f"Game data missing from save {saveNum}")

                difficulty = game.get('difficulty', 'normal')
                hardcore = game.get('hardcoreMode', False)

                difficultyObj = Difficulty(difficulty)
                diffDisplay = difficultyObj.getDisplayName()
                if hardcore:
                    diffDisplay += " [bold red](HARDCORE)[/bold red]"

                console.print(f"[cyan]{saveNum}.[/cyan] [bold]{playerName}[/bold] | [class_{className.lower()}]{className}[/class_{className.lower()}] | Level {playerLevel}")
                console.print(f"    [dim]Difficulty: {diffDisplay}[/dim]\n")
                saves.append(saveNum)
            except Exception as e:
                printError(f"Error loading Save {saveNum}: {e}")
                console.print(f"[cyan]{saveNum}.[/cyan] [dim](Corrupted Save File)[/dim]\n")

    return saves

def save(game, saveNum: int = 0, accountId: str = None):
    try:
        saveNum = int(saveNum)
    except ValueError:
        printError(f"Invalid save number: {saveNum}")
        pause()
        return
    
    if saveNum < 0:
        printError(f"Invalid save number: {saveNum}")
        pause()
        return
    
    savePath = _saveFilePath(saveNum, accountId)

    # if save already exists, show detail and confirm overwrite
    if exists(savePath):
        tmpJson = _tempJsonPath(saveNum, accountId)
        if _decodeKorus(savePath, tmpJson):
            try:
                with open(tmpJson, 'r') as f:
                    existingData = json.load(f)
                console.print(f"[warning]Save {saveNum} already exists![/warning]")
                console.print(
                    f"[dim]{existingData['player']['name']} "
                    f"(Level {existingData['player']['level']})[/dim]"
                )
            except Exception:
                console.print(f"[warning]Save {saveNum} already exists![/warning]")
            finally:
                if exists(tmpJson):
                    remove(tmpJson)
        else:
            console.print(f"[warning]Save {saveNum} exists but couldn't be read.[/warning]")

        confirm = console.input("[warning]Overwrite this save? (y/N): [/warning]").strip().lower()
        if confirm != 'y':
            printInfo("Save cancelled.")
            pause()
            return

        _createBackup(saveNum, accountId)

    try:
        saveData = {
            'player': game.player.serialise(),
            'camp': game.camp._serialiseAll(),
            'game': game._serialise()
        }
        ensureDirectories(accountId)

        try:
            from scripts.korusFeedClient import reportPlayerSave
            reportPlayerSave(game.player, saveNum, saveData['camp'], saveData['game'])
        except Exception:
            pass  # feed being unavailable should never block an actual save

        tmpJson = _tempJsonPath(saveNum, accountId)
        with open(tmpJson, 'w') as outFile:
            json.dump(saveData, outFile, indent=4)

        if _encodeKorus(tmpJson, savePath):
            printSuccess(f"Game saved to Save {saveNum}")
        else:
            # fallback — keep the JSON if encoding failed
            printInfo(f"Saved as JSON fallback: {tmpJson}")

        pause()
    except Exception as e:
        printError(f"Failed to save game: {e}")
        pause()

def load(saveNum: int, accountId: str = None):
    try:
        saveNum = int(saveNum)
    except ValueError:
        printError(f"Invalid save number: {saveNum}")
        pause()
        return {}

    savePath = _saveFilePath(saveNum, accountId)

    if saveNum < 0 or not exists(savePath):
        printError(f"Unable to find Save File: {saveNum}")
        pause()
        return {}

    tmpJson = _tempJsonPath(saveNum, accountId)

    if not _decodeKorus(savePath, tmpJson):
        pause()
        return {}

    try:
        with open(tmpJson, 'r') as inFile:
            saveData = json.load(inFile)
    except Exception as e:
        printError(f"Failed to read save data: {e}")
        pause()
        return {}
    finally:
        if exists(tmpJson):
            remove(tmpJson)

    console.print(f"[info]Found save file {saveNum}:[/info]")
    console.print(
        f"[dim]Player: {saveData['player']['name']} | "
        f"Class: {saveData['player']['className']} | {f'Ascendancy: {saveData['player']['ascendancy']} | ' if saveData['player']['ascendancy'] is not None else ''}"
        f"Level: {saveData['player']['level']}[/dim]"
    )

    confirm = console.input("[prompt]Load this save? (y/n): [/prompt]").strip().lower()
    if confirm == 'y':
        printSuccess(f"Data loaded from Save {saveNum}")
        pause()
        return {
            "player": saveData["player"],
            "camp":   saveData["camp"],
            "game":   saveData["game"]
        }
    else:
        printInfo("Load cancelled.")
        pause()
        return {}

def deleteSave(saveNum: int, accountId: str = None):
    try:
        saveNum = int(saveNum)
    except ValueError:
        printError(f"Invalid save number: {saveNum}")
        pause()
        return

    savePath = _saveFilePath(saveNum, accountId)

    if saveNum < 0 or not exists(savePath):
        printError(f"Unable to find Save File: {saveNum}")
        pause()
        return

    confirm = console.input(
        f"[warning]Are you sure you want to delete Save {saveNum}? (y/N): [/warning]"
    ).strip().lower()

    if confirm == 'y':
        try:
            _createBackup(saveNum, accountId)
            remove(savePath)
            printSuccess(f"Save {saveNum} successfully deleted.")
            pause()
        except Exception as e:
            printError(f"Failed to delete save: {e}")
            pause()

def checkForSaves(accountId: str = None) -> bool:
    ensureDirectories(accountId)
    savesRoot = _savesRoot(accountId)
    return any(isfile(join(savesRoot, f)) for f in listdir(savesRoot) if f.endswith('.korus'))

def addToDeathLog(game):
    try:
        ensureDirectories()
        deathTime    = datetime.now().strftime("%B %d %Y %H:%M:%S")
        deathLogPath = f"{PATH}Death Log.json"

        if not exists(deathLogPath):
            with open(deathLogPath, 'w') as f:
                json.dump({}, f)

        with open(deathLogPath, 'r') as f:
            try:
                allData = json.load(f)
            except json.JSONDecodeError:
                allData = {}

        allData[deathTime] = {
            "player": game.player.serialise(),
            "camp":   game.camp._serialiseAll(),
            "game":   game._serialise()
        }

        with open(deathLogPath, 'w') as f:
            json.dump(allData, f, indent=4)
            printInfo("Your death has been recorded into your death log.")
            pause()
    except Exception as e:
        printError(f"Failed to record death: {e}")
        pause()
