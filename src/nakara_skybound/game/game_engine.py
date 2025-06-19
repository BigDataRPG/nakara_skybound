from dataclasses import dataclass, field
from typing import Any, Dict, List

from .character import Player
from .magic_system import MagicSystem
from .memory_system import MemorySystem
from .narrative_engine import NarrativeEngine
from .time_system import TimeEra, TimeSystem
from .world import World


@dataclass
class GameState:
    current_era: TimeEra = TimeEra.PRESENT
    current_location: str = "central_plaza"
    current_scene: str = "game_start"
    player: Player = field(default_factory=Player)
    world_state: Dict[str, Any] = field(default_factory=dict)
    active_quests: List[str] = field(default_factory=list)
    time_fragments: int = 0
    loop_count: int = 0
    current_day: int = 1  # Track current day in the 7-day cycle
    decisions_made: List[Dict[str, Any]] = field(default_factory=list)


class GameEngine:
    def __init__(self):
        self.state = GameState()
        self.time_system = TimeSystem()
        self.world = World()
        self.magic_system = MagicSystem()
        self.memory_system = MemorySystem()
        self.narrative_engine = NarrativeEngine()

        # Initialize world
        self.world.initialize_locations()
        self.world.populate_npcs()

    def get_current_state(self) -> GameState:
        return self.state

    def make_decision(self, decision_id: str, choice: str) -> Dict[str, Any]:
        """Process player decision and update game state"""
        # Record the decision
        decision_record = {
            "id": decision_id,
            "choice": choice,
            "era": self.state.current_era,
            "location": self.state.current_location,
            "loop": self.state.loop_count,
            "day": self.state.current_day,
        }
        self.state.decisions_made.append(decision_record)

        # Store in memory system for future loops
        self.memory_system.store_decision(decision_record)

        # Get narrative response
        narrative_result = self.narrative_engine.process_decision(
            decision_record, self.state
        )

        # Update game state based on consequences (but don't auto-trigger loop)
        self._apply_consequences(narrative_result["consequences"])

        # Advance time slightly (but don't trigger loop automatically)
        # Only major story events should advance days
        if decision_id in ["major_quest_complete", "important_choice"]:
            self.state.current_day += 1

        # Check if 7 days have passed (but don't auto-trigger)
        if self.state.current_day > 7:
            narrative_result["day_cycle_complete"] = True
            narrative_result[
                "narrative"
            ] += "\n\n⏰ 7 วันได้ผ่านไปแล้ว... คุณรู้สึกว่าเวลากำลังจะรีเซ็ต"

        return narrative_result

    def travel_through_time(self, target_era: TimeEra) -> Dict[str, Any]:
        """Handle time travel between eras"""
        # Check if player can travel (stat requirements)
        if not self.time_system.can_travel_to_era(target_era, self.state.player):
            return {
                "success": False,
                "message": "ไม่สามารถเดินทางไปยุคนั้นได้ในตอนนี้ สถานะยังไม่เพียงพอ",
            }

        # Check time fragment requirements
        required_fragments = self.time_system.time_travel_requirements.get(
            target_era, {}
        ).get("time_fragments", 0)
        if (
            target_era != TimeEra.PRESENT
            and self.state.time_fragments < required_fragments
        ):
            return {
                "success": False,
                "message": f"ต้องการเศษเวลา {required_fragments} ชิ้น แต่คุณมีเพียง {self.state.time_fragments} ชิ้น",
            }

        # Store current era memories
        self.memory_system.store_era_state(self.state.current_era, self.state)

        # Change era
        old_era = self.state.current_era
        self.state.current_era = target_era

        # Consume time fragments
        if target_era != TimeEra.PRESENT:
            self.state.time_fragments -= required_fragments

        # Load era-specific world state
        era_state = self.memory_system.get_era_state(target_era)
        if era_state:
            self._apply_era_state(era_state)

        # Generate narrative for time travel
        travel_narrative = self.narrative_engine.generate_time_travel_scene(
            old_era, target_era, self.state
        )

        return {"success": True, "narrative": travel_narrative, "new_era": target_era}

    def trigger_time_loop(self) -> Dict[str, Any]:
        """Handle the 7-day time loop reset - only when explicitly called"""
        # Store current loop memories
        self.memory_system.store_loop_memories(self.state.loop_count, self.state)

        # Reset certain states but keep memories
        self.state.loop_count += 1
        self.state.current_day = 1  # Reset day counter
        self.state.current_location = "central_plaza"
        self.state.current_scene = "loop_reset"

        # NPCs remember previous loops
        self.world.update_npc_memories(self.memory_system.get_loop_memories())

        # Generate loop reset narrative
        loop_narrative = self.narrative_engine.generate_loop_reset_scene(
            self.state.loop_count, self.state
        )

        return {
            "success": True,
            "narrative": loop_narrative,
            "loop_count": self.state.loop_count,
        }

    def _apply_consequences(self, consequences: List[Dict[str, Any]]):
        """Apply decision consequences to game state"""
        for consequence in consequences:
            if consequence["type"] == "stat_change":
                self.state.player.modify_stat(consequence["stat"], consequence["value"])
            elif consequence["type"] == "item_gain":
                self.state.player.add_item(consequence["item"])
            elif consequence["type"] == "quest_update":
                self._update_quest(consequence["quest_id"], consequence["status"])
            elif consequence["type"] == "world_change":
                self.state.world_state[consequence["key"]] = consequence["value"]
            elif consequence["type"] == "time_fragment":
                self.state.time_fragments += consequence["amount"]

    def _apply_era_state(self, era_state: Dict[str, Any]):
        """Apply saved era state to current game state"""
        if "world_state" in era_state:
            self.state.world_state.update(era_state["world_state"])
        if "active_quests" in era_state:
            self.state.active_quests = era_state["active_quests"]

    def _update_quest(self, quest_id: str, status: str):
        """Update quest status"""
        if status == "started" and quest_id not in self.state.active_quests:
            self.state.active_quests.append(quest_id)
        elif status == "completed" and quest_id in self.state.active_quests:
            self.state.active_quests.remove(quest_id)
