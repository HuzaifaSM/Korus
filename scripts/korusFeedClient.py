import json
import re
import threading
import urllib.request
import urllib.error
import os
import subprocess
from typing import Optional
from .styles import printError, printSuccess

KORUS_FEED_ITEMS_URL = "http://localhost:8080/api/items"
KORUS_FEED_PLAYERS_URL = "http://localhost:8080/api/players"
TIMEOUT_SECONDS = 2

_TAG_RE = re.compile(r"\[/?[^\[\]]*\]")

def _stripMarkup(text: str) -> str:
    return _TAG_RE.sub("", text)

def _serialiseImplicits(implicits: dict) -> list:
    from scripts.items.equipment import PERCENT_IMPLICIT_STATS
    return [
        {'stat': stat, 'value': value, 'is_percent': stat in PERCENT_IMPLICIT_STATS}
        for stat, value in implicits.items()
    ]

def _serialiseAffix(affix) -> dict:
    return {
        "name": _stripMarkup(affix.name),
        "stat": affix.stat,
        "kind": affix.kind,
        "tier": affix.tier,
        "min_roll": affix.minVal,
        "max_roll": affix.maxVal,
        "base_value": affix.baseValue,
        "mastery": affix.mastery,
        "is_percent": affix.isPercent,
        "categories": affix.categories,
    }

def _serialiseDestabilisedAffixes(da) -> dict:
    return {
        'name': _stripMarkup(da.name),
        'stat': da.stat,
        'value': da.value,
        'is_percent': da.isPercent,
    }

def _serialiseMythicAffix(mythicAffix) -> Optional[dict]:
    if mythicAffix is None:
        return None
    return {
        "name": _stripMarkup(mythicAffix.name),
        "kind": mythicAffix.kind,
        "lines": [_stripMarkup(line.description) for line in mythicAffix.lines],
    }

def _serialiseEquipmentCore(equipment) -> dict:
    """Everything about an item that isn't context-dependent (who owns it / what just happened to it)."""
    affixes = []
    for slot in equipment.prefixSlots + equipment.suffixSlots:
        if slot.affix is not None:
            affixes.append(_serialiseAffix(slot.affix))

    return {
        "id": str(equipment.feedId),
        "name": _stripMarkup(equipment.name),
        "slot": equipment.slot,
        "rarity": equipment.rarity.value,
        "level": equipment.level,
        "base_item": equipment.baseTypeName or "",
        "mastery": equipment.mastery,
        "destabilised": equipment.destabilised,
        "affixes": affixes,
        "implicits": _serialiseImplicits(equipment.implicits),
        "destabilised_affixes": [_serialiseDestabilisedAffixes(da) for da in equipment.destabilisedAffixes],
        "damage": equipment.damage,
        "base_damage": equipment.baseDamage,
        "damage_type": equipment.damageType or "",
        "two_handed": equipment.twoHanded,
        "base_type": equipment.weaponType or equipment.sigilType or "",
        "defense_value": equipment.defenseValue,
        "base_defense_value": equipment.baseDefenseValue,
        "defense_type": equipment.defenseType or "",
        "durability": equipment.durability,
        "max_durability": equipment.maxDurability,
        "entropy": equipment.entropy,
        "max_entropy": equipment.maxEntropy,
        "entropy_resistance": equipment.entropyResistance,
        "entropy_locked": equipment.entropyLocked,
        "entropy_preserved": equipment.entropyPreserved,
        "num_preserved": equipment.numPreserved,
        "max_preservations": equipment.maxPreservations,
        "mythic_affix": _serialiseMythicAffix(equipment.mythicAffix),
    }

def _serialiseEquipment(equipment, playerName: str, event: str) -> dict:
    payload = _serialiseEquipmentCore(equipment)
    payload["player"] = playerName
    payload["event"] = _stripMarkup(event)
    return payload

def _serialiseConsumable(consumable) -> dict:
    return {
        "name": _stripMarkup(consumable.name),
        "heal_percent": consumable.healPercent,
    }

def _serialiseRune(runeKey: str, quantity: int) -> Optional[dict]:
    from scripts.runeDrops import getRuneObject

    parts = runeKey.split('_', 1)
    if len(parts) != 2:
        return None
    category, runeType = parts
    rune = getRuneObject(category, runeType)
    if rune is None:
        return None

    return {
        "key": runeKey,
        "name": _stripMarkup(rune.name),
        "description": _stripMarkup(rune.description),
        "entropy_added": rune.successEntropy,
        "min_affix_level": rune.minAffixLevel,
        "min_affix_tier": rune.minAffixTier,
        "min_item_level": rune.minItemLevel,
        "max_tier_delta": rune.maxTierDelta,
        "quantity": quantity,
    }

def _curateStation(raw: dict) -> dict:
    resourcesNeeded = dict(raw.get('resourcesNeeded') or {})
    bonus = _stripMarkup(resourcesNeeded.pop('description', ''))
    return {
        "name": raw.get('name', ''),
        "level": raw.get('level', 0),
        "resources_needed": resourcesNeeded,
        "next_level_bonus": bonus,
    }

def _curateCamp(campData: dict) -> dict:
    return {
        "campfire": _curateStation(campData.get('campfire', {})),
        "forge": _curateStation(campData.get('forge', {})),
        "market": _curateStation(campData.get('market', {})),
        "quest_board": _curateStation(campData.get('questBoard', {})),
        "shrine": _curateStation(campData.get('shrine', {})),
    }

def _curateGame(gameData: dict) -> dict:
    return {
        "area_level": gameData.get('areaLevel', 1),
        "battles_won": gameData.get('battlesWon', 0),
        "difficulty": gameData.get('difficulty', 'normal'),
        "hardcore_mode": gameData.get('hardcoreMode', False),
    }

def _serialisePlayer(player, saveNum: int, campData: Optional[dict], gameData: Optional[dict]) -> dict:
    equipped = {}
    for slot, equip in player._equipment.items():
        if equip is not None:
            equipped[slot] = _serialiseEquipmentCore(equip)

    equipmentStorage = [_serialiseEquipmentCore(equip) for equip in player._equipmentStorage if equip is not None]

    runes = []
    for runeKey, quantity in player._craftingInventory.items():
        rune = _serialiseRune(runeKey, quantity)
        if rune is not None:
            runes.append(rune)

    return {
        "save_num": saveNum,
        "name": _stripMarkup(player._name),
        "class_name": player.className or "",
        "class_description": _stripMarkup(player.classDescription or ""),
        "ascendancy": player._ascendancy or "",
        "ascendancy_description": _stripMarkup(player.ascendancyDescription or ""),
        "level": player._level,
        "xp": player._xp,
        "xp_to_next_level": player._xpToNextLevel,
        "max_level": player._maxLevel,
        "gold": player._gold,
        "max_health": player._maxHealth,
        "base_health": player._baseHealth,
        "health": player._health,
        "max_stamina": player._maxStamina,
        "base_max_stamina": player._baseMaxStamina,
        "stamina": player._stamina,
        "base_damage": player._baseDamage,
        "damage_type": player._damageType or "",
        "base_speed": round(player._baseSpeed, 2),
        "stats": player._stats,
        "equipped": equipped,
        "equipment_storage": equipmentStorage,
        "crafting_inventory": runes,
        "inventory": player._inventory,
        "consumable": _serialiseConsumable(player.consumable),
        "camp": _curateCamp(campData) if campData else None,
        "game": _curateGame(gameData) if gameData else None,
    }

def _postInBackground(payload: dict, url: str):
    def _send():
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS)
        except urllib.error.HTTPError as e:
            # the server was reached but rejected the payload - a real bug,
            try:
                body = e.read().decode(errors='replace')
            except Exception:
                body = ""
            printError(f"[dim]Korus Feed rejected a report ({e.code}): {body}[/dim]")
        except Exception:
            pass # offline/not working doesn't affect gameplay

    threading.Thread(target=_send, daemon=True).start()

def reportItem(equipment, playerName: str, event: str = "Created"):
    if not playerName:
        return
    _postInBackground(_serialiseEquipment(equipment, playerName, event), KORUS_FEED_ITEMS_URL)

def reportPlayerSave(player, saveNum: int, campData: Optional[dict] = None, gameData: Optional[dict] = None):
    try:
        payload = _serialisePlayer(player, saveNum, campData, gameData)
    except Exception:
        return
    _postInBackground(payload, KORUS_FEED_PLAYERS_URL)

def ensureServerRunning():
    try:
        urllib.request.urlopen("http://localhost:8080/health", timeout=0.5)
        printSuccess('[dim]Korus Feed running. Server link: http://localhost:8080 [/dim]')
        return
    except Exception:
        pass

    try:
        feedDir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'Korus_Feed'))
        exePath = os.path.join(feedDir, 'korusfeed.exe')
        if not os.path.isfile(exePath):
            return

        flags = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        subprocess.Popen(
            [exePath],
            cwd=feedDir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=flags
        )
        printSuccess('[dim]Korus Feed running. Server link: http://localhost:8080 [/dim]')
    except Exception as e:
        printError(f'[dim]Error opening Korus Feed: {e}[/dim]')

def isServerRunning() -> bool:
    try:
        urllib.request.urlopen("http://localhost:8080/health", timeout=0.5)
        return True
    except Exception:
        return False

...