import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

from .character import CharacterClass, Item, Player, Stats
from .game_engine import GameState


class SaveSystem:
    def __init__(self, save_directory: str = "saves"):
        self.save_directory = save_directory
        self.ensure_save_directory()

    def ensure_save_directory(self):
        """Create save directory if it doesn't exist"""
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)

    def save_game(self, game_state: GameState, save_name: str = None) -> bool:
        """Save current game state"""
        if save_name is None:
            save_name = f"save_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        try:
            save_data = self._serialize_game_state(game_state)
            save_path = os.path.join(self.save_directory, f"{save_name}.json")

            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    def load_game(self, save_name: str) -> Optional[GameState]:
        """Load game state from save file"""
        try:
            save_path = os.path.join(self.save_directory, f"{save_name}.json")

            if not os.path.exists(save_path):
                return None

            with open(save_path, "r", encoding="utf-8") as f:
                save_data = json.load(f)

            return self._deserialize_game_state(save_data)
        except Exception as e:
            print(f"Error loading game: {e}")
            return None

    def list_saves(self) -> list[Dict[str, Any]]:
        """List all available save files"""
        saves = []

        for filename in os.listdir(self.save_directory):
            if filename.endswith(".json"):
                save_name = filename[:-5]  # Remove .json extension
                save_path = os.path.join(self.save_directory, filename)

                try:
                    # Get file modification time
                    mod_time = os.path.getmtime(save_path)
                    mod_datetime = datetime.fromtimestamp(mod_time)

                    # Try to get some basic info from the save
                    with open(save_path, "r", encoding="utf-8") as f:
                        save_data = json.load(f)

                    saves.append(
                        {
                            "name": save_name,
                            "date": mod_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                            "player_name": save_data.get("player", {}).get(
                                "name", "Unknown"
                            ),
                            "loop_count": save_data.get("loop_count", 0),
                            "current_era": save_data.get("current_era", "present"),
                        }
                    )
                except Exception:
                    # Skip corrupted saves
                    continue

        # Sort by modification time, newest first
        saves.sort(key=lambda x: x["date"], reverse=True)
        return saves

    def delete_save(self, save_name: str) -> bool:
        """Delete a save file"""
        try:
            save_path = os.path.join(self.save_directory, f"{save_name}.json")
            if os.path.exists(save_path):
                os.remove(save_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting save: {e}")
            return False

    def _serialize_game_state(self, game_state: GameState) -> Dict[str, Any]:
        """Convert game state to serializable dictionary"""
        return {
            "current_era": game_state.current_era.value,
            "current_location": game_state.current_location,
            "current_scene": game_state.current_scene,
            "player": self._serialize_player(game_state.player),
            "world_state": game_state.world_state,
            "active_quests": game_state.active_quests,
            "time_fragments": game_state.time_fragments,
            "loop_count": game_state.loop_count,
            "decisions_made": game_state.decisions_made,
            "save_timestamp": datetime.now().isoformat(),
        }

    def _serialize_player(self, player: Player) -> Dict[str, Any]:
        """Convert player to serializable dictionary"""
        return {
            "name": player.name,
            "character_class": player.character_class.value,
            "stats": {
                "wisdom": player.stats.wisdom,
                "strength": player.stats.strength,
                "karma": player.stats.karma,
                "mysticism": player.stats.mysticism,
                "charisma": player.stats.charisma,
            },
            "level": player.level,
            "experience": player.experience,
            "time_fragments": player.time_fragments,
            "inventory": [self._serialize_item(item) for item in player.inventory],
            "learned_spells": player.learned_spells,
            "memory_fragments": player.memory_fragments,
        }

    def _serialize_item(self, item: Item) -> Dict[str, Any]:
        """Convert item to serializable dictionary"""
        return {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "type": item.type,
            "power": item.power,
            "magical_properties": item.magical_properties,
        }

    def _deserialize_game_state(self, save_data: Dict[str, Any]) -> GameState:
        """Convert serialized data back to game state"""
        from .time_system import TimeEra  # Import here to avoid circular imports

        game_state = GameState()
        game_state.current_era = TimeEra(save_data["current_era"])
        game_state.current_location = save_data["current_location"]
        game_state.current_scene = save_data["current_scene"]
        game_state.player = self._deserialize_player(save_data["player"])
        game_state.world_state = save_data["world_state"]
        game_state.active_quests = save_data["active_quests"]
        game_state.time_fragments = save_data["time_fragments"]
        game_state.loop_count = save_data["loop_count"]
        game_state.decisions_made = save_data["decisions_made"]

        return game_state

    def _deserialize_player(self, player_data: Dict[str, Any]) -> Player:
        """Convert serialized data back to player"""
        player = Player(
            name=player_data["name"],
            character_class=CharacterClass(player_data["character_class"]),
        )

        # Restore stats
        stats_data = player_data["stats"]
        player.stats = Stats(
            wisdom=stats_data["wisdom"],
            strength=stats_data["strength"],
            karma=stats_data["karma"],
            mysticism=stats_data["mysticism"],
            charisma=stats_data["charisma"],
        )

        player.level = player_data["level"]
        player.experience = player_data["experience"]
        player.time_fragments = player_data["time_fragments"]
        player.learned_spells = player_data["learned_spells"]
        player.memory_fragments = player_data["memory_fragments"]

        # Restore inventory
        player.inventory = [
            self._deserialize_item(item_data) for item_data in player_data["inventory"]
        ]

        return player

    def _deserialize_item(self, item_data: Dict[str, Any]) -> Item:
        """Convert serialized data back to item"""
        return Item(
            id=item_data["id"],
            name=item_data["name"],
            description=item_data["description"],
            type=item_data["type"],
            power=item_data["power"],
            magical_properties=item_data["magical_properties"],
        )
