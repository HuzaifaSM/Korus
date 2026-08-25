from typing import Dict

from scripts.styles import (
    console, pause, printWarning, clearScreen
)

from .player_classes.classes import CLASSES, DESCRIPTIONS
from .player_classes.base import Player

def selectClass(name: str, quick: bool = False) -> Player:
    if quick:
        return CLASSES['Warrior'](name)
    while True:
        clearScreen()
        console.print("\n[bold cyan]=== Class Select ===[/bold cyan]")
        for i, (classType, _) in enumerate(CLASSES.items(), 1):
            console.print(f"  [cyan]{i}:[/cyan] {classType}")
        console.print("\n[dim]Type a number to see class description, or select to play[/dim]")
        choice = console.input("[cyan]What class do you want to play?[/cyan]\n> ").strip()
        try:
            choice = int(choice) - 1
            if 0 <= choice < len(CLASSES):
                chosen = list(CLASSES.keys())[choice]
                
                # Show description
                console.print(f"\n[bold gold1]{chosen}[/bold gold1]")
                console.print(f"{DESCRIPTIONS[chosen][chosen]}\n")

                confirm = console.input("[cyan]Play as this class? (y/n):[/cyan] ").strip().lower()
                if confirm == 'y':
                    return CLASSES[chosen](name)
        except (ValueError, IndexError):
            printWarning("Invalid choice. Please try again.")

def deserialisePlayer(data: Dict) -> Player:
    className = data.get('className')
    playerName = data.get('name', 'The Hero')

    if not className or className not in CLASSES:
        printWarning(f"ERROR LOADING SAVE DATA: {className=}")
        pause()
        return
    else:
        player: Player = CLASSES[className](playerName)

    player.deserialise(data)

    return player

...