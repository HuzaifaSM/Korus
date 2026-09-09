import json
import re
import threading
import urllib.request
import os
import subprocess

KORUS_FEED_URL = "http://localhost:8080/items"
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

def _serialiseEquipment(equipment, playerName: str, event: str) -> dict:
    affixes = []
    for slot in equipment.prefixSlots + equipment.suffixSlots:
        if slot.affix is not None:
            affixes.append(_serialiseAffix(slot.affix))

    return {
        "id": str(equipment.feedId),
        "name": _stripMarkup(equipment.name),
        "player": playerName,
        "slot": equipment.slot,
        "rarity": equipment.rarity.value,
        "level": equipment.level,
        "base_type": equipment.baseTypeName or "",
        "mastery": equipment.mastery,
        "destabilised": equipment.destabilised,
        "affixes": affixes,
        "implicits": _serialiseImplicits(equipment.implicits),
        "destabilised_affixes": [_serialiseDestabilisedAffixes(da) for da in equipment.destabilisedAffixes],
        "damage": equipment.damage,
        "base_damage": equipment.baseDamage,
        "damage_type": equipment.damageType or "",
        "two_handed": equipment.twoHanded,
        "weapon_type": equipment.weaponType or "",
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
        "sigil_type": equipment.sigilType or "",
        "event": _stripMarkup(event),
    }

def _postInBackground(payload: dict):
    def _send():
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                KORUS_FEED_URL,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS)
        except Exception:
            pass # offline/not working doesn't affect gameplay

    threading.Thread(target=_send, daemon=True).start()

def reportItem(equipment, playerName: str, event: str = "Created"):
    if not playerName:
        return
    _postInBackground(_serialiseEquipment(equipment, playerName, event))

def ensureServerRunning():
    try:
        urllib.request.urlopen("http://localhost:8080/health", timeout=0.5)
        return
    except Exception:
        pass

    try:
        feedDir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'Korus_Feed'))
        if not os.path.isdir(feedDir):
            return

        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        subprocess.Popen(
            {'go', 'run', '.cmd/server'},
            cwd=feedDir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=flags
        )
    except Exception:
        pass

...