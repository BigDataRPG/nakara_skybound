from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class CharacterClass(Enum):
    SAGE = "sage"  # นักปราชญ์
    WARRIOR = "warrior"  # นักรบ
    MYSTIC = "mystic"  # นักเวทย์


@dataclass
class Stats:
    wisdom: int = 10  # ปัญญา
    strength: int = 10  # กำลัง
    karma: int = 0  # กรรม (can be negative)
    mysticism: int = 10  # เวทมนตร์
    charisma: int = 10  # เสน่ห์


@dataclass
class Item:
    id: str
    name: str
    description: str
    type: str
    power: int = 0
    magical_properties: Dict[str, Any] = field(default_factory=dict)


class Player:
    def __init__(
        self,
        name: str = "ผู้เดินทาง",
        character_class: CharacterClass = CharacterClass.SAGE,
    ):
        self.name = name
        self.character_class = character_class
        self.stats = Stats()
        self.level = 1
        self.experience = 0
        self.time_fragments = 0
        self.inventory: List[Item] = []
        self.learned_spells: List[str] = []
        self.memory_fragments: List[Dict[str, Any]] = []

        # Set initial stats based on class
        self._set_class_stats()

    def _set_class_stats(self):
        """Set initial stats based on character class"""
        if self.character_class == CharacterClass.SAGE:
            self.stats.wisdom += 5
            self.stats.mysticism += 3
        elif self.character_class == CharacterClass.WARRIOR:
            self.stats.strength += 5
            self.stats.charisma += 3
        elif self.character_class == CharacterClass.MYSTIC:
            self.stats.mysticism += 5
            self.stats.wisdom += 3

    def modify_stat(self, stat_name: str, value: int):
        """Modify a character stat"""
        if hasattr(self.stats, stat_name):
            current_value = getattr(self.stats, stat_name)
            setattr(self.stats, stat_name, current_value + value)

    def add_item(self, item: Item):
        """Add item to inventory"""
        self.inventory.append(item)

    def remove_item(self, item_id: str) -> bool:
        """Remove item from inventory"""
        for i, item in enumerate(self.inventory):
            if item.id == item_id:
                del self.inventory[i]
                return True
        return False

    def learn_spell(self, spell_id: str):
        """Learn a new spell"""
        if spell_id not in self.learned_spells:
            self.learned_spells.append(spell_id)

    def add_memory_fragment(self, memory: Dict[str, Any]):
        """Add a memory fragment from previous loops"""
        self.memory_fragments.append(memory)

    def get_total_power(self) -> int:
        """Calculate total power including items"""
        base_power = sum(
            [
                self.stats.wisdom,
                self.stats.strength,
                self.stats.mysticism,
                self.stats.charisma,
            ]
        )

        item_power = sum([item.power for item in self.inventory])

        return base_power + item_power


@dataclass
class NPCMemory:
    player_actions: List[Dict[str, Any]] = field(default_factory=list)
    relationship_level: int = 0
    trust_level: int = 0
    last_interaction_loop: int = -1
    secrets_revealed: List[str] = field(default_factory=list)


class NPC:
    def __init__(self, id: str, name: str, role: str, location: str):
        self.id = id
        self.name = name
        self.role = role
        self.location = location
        self.stats = Stats()
        self.personality_traits: List[str] = []
        self.dialogue_states: Dict[str, Any] = {}
        self.memory = NPCMemory()
        self.available_quests: List[str] = []
        self.special_abilities: List[str] = []

    def remember_player_action(self, action: Dict[str, Any]):
        """Remember a player action from current or previous loops"""
        self.memory.player_actions.append(action)

        # Adjust relationship based on action
        if action.get("karma_impact", 0) > 0:
            self.memory.relationship_level += 1
            self.memory.trust_level += 1
        elif action.get("karma_impact", 0) < 0:
            self.memory.relationship_level -= 1
            self.memory.trust_level -= 2

    def get_dialogue_options(
        self, player_state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get available dialogue options based on memory and relationship"""
        options = []

        # Basic greeting
        if self.memory.last_interaction_loop < player_state.get("current_loop", 0):
            if self.memory.relationship_level > 5:
                options.append(
                    {
                        "id": "friendly_greeting",
                        "text": f"สวัสดี {player_state.get('player_name', 'ผู้เดินทาง')} เราเจอกันอีกแล้วนะ",
                        "requires": None,
                    }
                )
            else:
                options.append(
                    {
                        "id": "neutral_greeting",
                        "text": "สวัสดี ท่านคือใคร?",
                        "requires": None,
                    }
                )

        # Quest-related options
        for quest_id in self.available_quests:
            if quest_id not in player_state.get("completed_quests", []):
                options.append(
                    {
                        "id": f"quest_{quest_id}",
                        "text": f"เกี่ยวกับ{quest_id}...",
                        "requires": {"trust_level": 3},
                    }
                )

        # Memory-based options
        if len(self.memory.player_actions) > 0:
            options.append(
                {
                    "id": "remember_past",
                    "text": "ฉันจำได้ว่าเธอเคย...",
                    "requires": {"relationship_level": 7},
                }
            )

        return options

    def update_memory_from_loop(self, loop_memories: List[Dict[str, Any]]):
        """Update NPC memory based on previous loop experiences"""
        for memory in loop_memories:
            if memory.get("npc_id") == self.id:
                self.remember_player_action(memory)
