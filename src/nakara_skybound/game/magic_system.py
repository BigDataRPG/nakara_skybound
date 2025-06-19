from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List

from .character import Player


class MagicType(Enum):
    YANTRA = "yantra"  # ยันต์
    MANTRA = "mantra"  # มนตร์
    MUDRA = "mudra"  # มุทรา
    BLESSING = "blessing"  # พร


@dataclass
class Spell:
    id: str
    name: str
    description: str
    magic_type: MagicType
    power_required: int
    karma_cost: int
    effects: List[Dict[str, Any]] = field(default_factory=list)
    requirements: Dict[str, int] = field(default_factory=dict)


class MagicSystem:
    def __init__(self):
        self.available_spells = self._initialize_spells()
        self.spell_combinations = {}

    def _initialize_spells(self) -> Dict[str, Spell]:
        """Initialize basic Thai magic spells"""
        spells = {
            "protection_yantra": Spell(
                id="protection_yantra",
                name="ยันต์ป้องกัน",
                description="ยันต์โบราณที่ช่วยป้องกันอันตราย",
                magic_type=MagicType.YANTRA,
                power_required=10,
                karma_cost=0,
                effects=[{"type": "protection", "value": 5}],
                requirements={"mysticism": 15},
            ),
            "time_glimpse": Spell(
                id="time_glimpse",
                name="มนต์แลเวลา",
                description="มนต์ที่ให้เห็นเศษเวลาในอนาคตหรือในอดีต",
                magic_type=MagicType.MANTRA,
                power_required=20,
                karma_cost=1,
                effects=[{"type": "vision", "target": "time_fragment"}],
                requirements={"wisdom": 20, "mysticism": 25},
            ),
            "karma_cleanse": Spell(
                id="karma_cleanse",
                name="พิธีชำระกรรม",
                description="พิธีกรรมโบราณที่ช่วยลดกรรมลบ",
                magic_type=MagicType.BLESSING,
                power_required=30,
                karma_cost=-5,  # Actually reduces karma
                effects=[{"type": "karma_change", "value": -10}],
                requirements={"wisdom": 30, "charisma": 25},
            ),
        }
        return spells

    def can_cast_spell(self, spell_id: str, player: Player) -> bool:
        """Check if player can cast a spell"""
        if spell_id not in self.available_spells:
            return False

        spell = self.available_spells[spell_id]

        # Check if player knows the spell
        if spell_id not in player.learned_spells:
            return False

        # Check requirements
        for stat, required_value in spell.requirements.items():
            if getattr(player.stats, stat, 0) < required_value:
                return False

        # Check if player has enough mysticism power
        if player.stats.mysticism < spell.power_required:
            return False

        return True

    def cast_spell(self, spell_id: str, player: Player) -> Dict[str, Any]:
        """Cast a spell and return results"""
        if not self.can_cast_spell(spell_id, player):
            return {"success": False, "message": "ไม่สามารถใช้เวทมนตร์นี้ได้"}

        spell = self.available_spells[spell_id]

        # Apply karma cost
        player.modify_stat("karma", spell.karma_cost)

        # Apply spell effects
        results = []
        for effect in spell.effects:
            if effect["type"] == "protection":
                results.append(f"ได้รับการป้องกัน +{effect['value']}")
            elif effect["type"] == "vision":
                results.append("ได้เห็นนิมิตแห่งเวลา...")
            elif effect["type"] == "karma_change":
                player.modify_stat("karma", effect["value"])
                results.append(f"กรรมเปลี่ยนแปลง {effect['value']}")

        return {
            "success": True,
            "spell_name": spell.name,
            "effects": results,
            "narrative": f"คุณร่ายเวทมนตร์ {spell.name} พลังเวทย์ไหลผ่านร่างกาย...",
        }

    def learn_spell(self, spell_id: str, player: Player) -> bool:
        """Learn a new spell"""
        if spell_id in self.available_spells and spell_id not in player.learned_spells:
            spell = self.available_spells[spell_id]

            # Check if player meets requirements to learn
            for stat, required_value in spell.requirements.items():
                if (
                    getattr(player.stats, stat, 0) < required_value - 5
                ):  # Can learn 5 points before requirement
                    return False

            player.learn_spell(spell_id)
            return True
        return False

    def get_available_spells_for_player(self, player: Player) -> List[Spell]:
        """Get spells that player can potentially learn or cast"""
        available = []
        for spell in self.available_spells.values():
            # Check if requirements are close to being met
            can_learn = True
            for stat, required_value in spell.requirements.items():
                if getattr(player.stats, stat, 0) < required_value - 10:
                    can_learn = False
                    break

            if can_learn:
                available.append(spell)

        return available
