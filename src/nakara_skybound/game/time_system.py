from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class TimeEra(Enum):
    PAST = "past"
    PRESENT = "present"
    FUTURE = "future"


@dataclass
class TimeFragment:
    id: str
    name: str
    description: str
    power: int
    era_origin: TimeEra


class TimeSystem:
    def __init__(self):
        self.era_descriptions = {
            TimeEra.PAST: {
                "name": "อดีตกาล - ยุคทองของอัษฎานคร",
                "description": "ดินแดนแห่งเวทมนตร์และตำนาน ที่มนุษย์และเทพยดาอยู่ร่วมกัน",
                "atmosphere": "mystical_ancient",
            },
            TimeEra.PRESENT: {
                "name": "ปัจจุบันกาล - ยุคแห่งการเปลี่ยนแปลง",
                "description": "โลกที่เทคโนโลยีและเวทมนตร์ผสมผสาน ความขัดแย้งเริ่มปรากฏ",
                "atmosphere": "modern_conflict",
            },
            TimeEra.FUTURE: {
                "name": "อนาคตกาล - ยุคแห่งผลลัพธ์",
                "description": "โลกที่เปลี่ยนไปตามการตัดสินใจในอดีต บางทีอาจจะดีหรือเลวร้าย",
                "atmosphere": "dystopian_or_utopian",
            },
        }

        self.time_travel_requirements = {
            TimeEra.PAST: {"time_fragments": 3, "wisdom": 10},
            TimeEra.FUTURE: {"time_fragments": 5, "karma": 0},  # Karma can be negative
        }

    def can_travel_to_era(self, target_era: TimeEra, player) -> bool:
        """Check if player can travel to target era"""
        if target_era == TimeEra.PRESENT:
            return True  # Can always return to present

        requirements = self.time_travel_requirements.get(target_era, {})

        # Check time fragments from game state, not player
        if "time_fragments" in requirements:
            # This will be checked by the game engine using state.time_fragments
            pass

        # Check stats
        for stat, required_value in requirements.items():
            if stat == "time_fragments":
                continue

            player_value = getattr(player.stats, stat, 0)
            if stat == "karma":
                # Karma can be any value (positive or negative)
                continue
            elif player_value < required_value:
                return False

        return True

    def get_era_info(self, era: TimeEra) -> Dict[str, str]:
        """Get information about a specific era"""
        return self.era_descriptions.get(era, {})

    def calculate_time_travel_cost(
        self, current_era: TimeEra, target_era: TimeEra
    ) -> int:
        """Calculate the cost in time fragments for time travel"""
        if target_era == TimeEra.PRESENT:
            return 1  # Always costs 1 fragment to return to present

        era_distances = {
            (TimeEra.PRESENT, TimeEra.PAST): 3,
            (TimeEra.PRESENT, TimeEra.FUTURE): 5,
            (TimeEra.PAST, TimeEra.FUTURE): 8,
            (TimeEra.FUTURE, TimeEra.PAST): 8,
        }

        return era_distances.get((current_era, target_era), 1)

    def get_available_eras(self, player) -> List[TimeEra]:
        """Get list of eras the player can currently travel to"""
        available = [TimeEra.PRESENT]  # Always available

        for era in [TimeEra.PAST, TimeEra.FUTURE]:
            if self.can_travel_to_era(era, player):
                available.append(era)

        return available
