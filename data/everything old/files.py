import json
import traceback
from os.path import exists, isfile, join
from os import remove, listdir, makedirs
from datetime import datetime
from shutil import copy2
from .styles import console, printSuccess, printError, printInfo, pause

if exists('Korus'):
    PATH = "Korus/data/saves/"
    LOGS = "Korus/data/logs/"
    BACKUP_PATH = "Korus/data/saves/.backup/"
else:
    PATH = "data/saves/"
    LOGS = "data/logs/"
    BACKUP_PATH = "data/saves/.backup/"

def ensure_directories():
    makedirs(PATH, exist_ok=True)
    makedirs(LOGS, exist_ok=True)
    makedirs(BACKUP_PATH, exist_ok=True)

def logCrash(exception: Exception, game=None):
    ensure_directories()
    crashTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    crash_filename = datetime.now().strftime("%Y%m%d_%H%M%S")
    # exception details
    crashData = {
        "timestamp": crashTime,
        "exception_type": type(exception).__name__,
        "exception_message": str(exception),
        "traceback": traceback.format_exc(),
        "game_state_saved": False
    }
    if game and hasattr(game, 'player') and game.player:
        try:
            p = game.player._serialise()
            c = game.camp._serialiseAll()
            g = game._serialise()
            saveData = {
                "player": p,
                "camp": c,
                "game": g
            }
            with open(f"{LOGS}Crash Save {crash_filename}.json", 'w') as outFile:
                json.dump(saveData, outFile, indent=4)

            crashData["game_state_saved"] = True
            crashData["crash_save_file"] = f"{LOGS}Crash Save {crash_filename}"
            crashData["player_name"] = game.player._name
            crashData["player_level"] = game.player._level
            crashData["battles_won"] = game.battlesWon
        except Exception as save_error:
            crashData["game_state_save_error"] = str(save_error)
    # write crash log
    crash_log_path = f"{LOGS}crash_{crash_filename}.log"
    with open(crash_log_path, 'w') as logFile:
        logFile.write("="*70 + "\n")
        logFile.write(f"CRASH REPORT - {crashTime}\n")
        logFile.write("="*70 + "\n")
        logFile.write(f"Exception Type: {crashData['exception_type']}\n")
        logFile.write(f"Exception Message: {crashData['exception_message']}\n\n")
        
        if crashData.get('player_name'):
            logFile.write(f"Player: {crashData['player_name']} (Level {crashData['player_level']})\n")
            logFile.write(f"Battles Won: {crashData['battles_won']}\n\n")
        
        logFile.write("Full Traceback:\n")
        logFile.write("-" * 70 + "\n")
        logFile.write(crashData['traceback'])
        logFile.write("-" * 70 + "\n\n")
        
        if crashData['game_state_saved']:
            logFile.write(f"Game state saved to: {crashData['crash_save_file']}\n")
        elif 'game_state_save_error' in crashData:
            logFile.write(f"Failed to save game state: {crashData['game_state_save_error']}\n")
        # save as json for easier parsing
        crash_json_path = f"{LOGS}crash_{crash_filename}.json"
        with open(crash_json_path, 'w') as jsonFile:
            json.dump(crashData, jsonFile, indent=4)

    return crash_log_path, crash_json_path

def _createBackup(saveNum: int) -> bool:
    savePath = f"{PATH}Save {saveNum}.json"
    if exists(savePath):
        try:
            ensure_directories()
            backupPath = f"{BACKUP_PATH}Save {saveNum}.backup.json"
            copy2(savePath, backupPath)
            return True
        except Exception as e:
            printError(f"Failed to create backup: {e}")
            return False
    return False

def undoLastOperation() -> bool:
    ensure_directories()

    if not exists(BACKUP_PATH):
        printError("No backup available to undo.")
        pause()
        return False

    backups = [f for f in listdir(BACKUP_PATH) if f.endswith('.backup.json')]

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
            printInfo("Undo Cancelled.")
            pause()
            return False
        
        backupPath = f"{BACKUP_PATH}Save {saveNum}.backup.json"
        savePath = f"{PATH}Save {saveNum}.json"
        
        if not exists(backupPath):
            printError(f"No backup found for Save {saveNum}.")
            pause()
            return False
        
        confirm = console.input(f"[warning]Restore Save {saveNum} from backup? This will overwrite the current save. (y/N): [/warning]").strip().lower()
        
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

def save(game, saveNum: int = 0):
    try:
        saveNum = int(saveNum)
    except ValueError:
        printError(f"Invalid save number: {saveNum}")
        pause()
        return
        
    if saveNum > -1:
        try:
            savePath = f"{PATH}Save {saveNum}.json"
            if exists(savePath):
                try:
                    with open(savePath, 'r') as existingFile:
                        existingData = json.load(existingFile)
                        existingPlayerName = existingData['player']['name']
                        existingPlayerLevel = existingData['player']['level']
                    
                    console.print(f"[warning]Save {saveNum} already exists![/warning]")
                    console.print(f"[dim]Current save: {existingPlayerName} (Level {existingPlayerLevel})[/dim]")
                    confirm = console.input("[warning]Overwrite this save? (y/N): [/warning]").strip().lower()
                    
                    if confirm != 'y':
                        printInfo("Save cancelled.")
                        pause()
                        return
                    
                    _createBackup(saveNum)
                except Exception as e:
                    confirm = console.input(f"[warning]Save {saveNum} exists but couldn't be read. Overwrite? (y/N): [/warning]").strip().lower()
                    if confirm != 'y':
                        printInfo("Save cancelled.")
                        pause()
                        return

            p = game.player._serialise()
            c = game.camp._serialiseAll()
            g = game._serialise()
            saveData = {
                "player": p,
                "camp": c,
                "game": g
            }
            
            ensure_directories()
            
            with open(f"{PATH}Save {saveNum}.json", 'w') as outFile:
                json.dump(saveData, outFile, indent=4)
                printSuccess(f"Game saved to Save {saveNum}")
                pause()
        except Exception as e:
            printError(f"Failed to save game: {e}")
            pause()
    else:
        printError(f"Invalid Save Number: {saveNum}")
        pause()

def load(saveNum: int):
    try:
        saveNum = int(saveNum)
    except ValueError:
        printError(f"Invalid save number: {saveNum}")
        pause()
        return {}
    
    savePath = f"{PATH}Save {saveNum}.json"
        
    if saveNum > -1 and exists(savePath):
        try:
            with open(savePath, 'r') as inFile:
                saveData = json.load(inFile)
                
            console.print(f"[info]Found save file {saveNum}:[/info]")
            console.print(f"[dim]Player: {saveData['player']['name']} | Class: {saveData['player']['className']} | Level: {saveData['player']['level']}[/dim]")
            
            confirm = console.input("[prompt]Load this save? (y/n): [/prompt]").strip().lower()
            
            if confirm == 'y':
                printSuccess(f"Data loaded from Save {saveNum}")
                console.print(f"[dim]Player: {saveData['player']['name']} | Level: {saveData['player']['level']}[/dim]")
                pause()
                return {
                    "player": saveData["player"],
                    "camp": saveData["camp"],
                    "game": saveData["game"]
                }
            else:
                printInfo("Load Cancelled")
                pause()
                return {}
            
        except Exception as e:
            printError(f"Failed to load save: {e}")
            pause()
            return {}
    else:
        printError(f"Unable to find Save File: {saveNum}")
        pause()
        return {}

def deleteSave(saveNum: int):
    try:
        saveNum = int(saveNum)
    except ValueError:
        printError(f"Invalid save number: {saveNum}")
        pause()
        return
        
    if saveNum > -1 and exists(f"{PATH}Save {saveNum}.json"):
        confirm = console.input(f"[warning]Are you sure you want to delete Save {saveNum}? (y/N): [/warning]").strip().lower()
        if confirm == 'y':
            try:
                # Create backup before deleting
                _createBackup(saveNum)
                remove(f"{PATH}Save {saveNum}.json")
                printSuccess(f"Save {saveNum} successfully deleted.")
                pause()
            except Exception as e:
                printError(f"Failed to delete save: {e}")
                pause()
    else:
        printError(f"Unable to find Save File: {saveNum}")
        pause()

def checkForSaves() -> bool:
    ensure_directories()
    return any(isfile(join(PATH, f)) for f in listdir(PATH) if f.endswith('.json'))

def addToDeathLog(game):
    try:
        ensure_directories()
        
        p = game.player._serialise()
        c = game.camp._serialiseAll()
        g = game._serialise()
        deathTime = datetime.now().strftime("%B %d %Y %H:%M:%S")
        
        deathLogPath = f"{PATH}Death Log.json"
        
        # Create death log if it doesn't exist
        if not exists(deathLogPath):
            with open(deathLogPath, 'w') as deathLog:
                json.dump({}, deathLog)
        
        # Load existing data
        with open(deathLogPath, 'r') as deathLog:
            try:
                allData = json.load(deathLog)
            except json.JSONDecodeError:
                allData = {}
        
        # Add new death
        allData[deathTime] = {
            "player": p,
            "camp": c,
            "game": g
        }
        
        # Save updated data
        with open(deathLogPath, 'w') as deathLog:
            json.dump(allData, deathLog, indent=4)
            printInfo("Your death has been recorded into your death log.")
            pause()
    except Exception as e:
        printError(f"Failed to record death: {e}")
        pause()

...