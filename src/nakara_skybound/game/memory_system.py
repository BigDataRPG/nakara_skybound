import json
from dataclasses import dataclass, field
from typing import Any, Dict, List

from .time_system import TimeEra


@dataclass
class MemoryFragment:
    id: str
    content: Dict[str, Any]
    era: TimeEra
    loop_number: int
    importance: int = 1  # 1-10 scale


class MemorySystem:
    def __init__(self):
        self.decision_memories: List[Dict[str, Any]] = []
        self.era_states: Dict[TimeEra, Dict[str, Any]] = {}
        self.loop_memories: Dict[int, Dict[str, Any]] = {}
        self.npc_memories: Dict[str, List[Dict[str, Any]]] = {}
        self.important_events: List[MemoryFragment] = []

    def store_decision(self, decision: Dict[str, Any]):
        """Store a player decision for future reference"""
        self.decision_memories.append(decision.copy())

        # If it's an important decision, create a memory fragment
        if decision.get("importance", 0) > 5:
            fragment = MemoryFragment(
                id=f"decision_{len(self.decision_memories)}",
                content=decision,
                era=decision.get("era", TimeEra.PRESENT),
                loop_number=decision.get("loop", 0),
                importance=decision.get("importance", 1),
            )
            self.important_events.append(fragment)

    def store_era_state(self, era: TimeEra, game_state):
        """Store the current state of an era"""
        era_data = {
            "world_state": game_state.world_state.copy(),
            "active_quests": game_state.active_quests.copy(),
            "location": game_state.current_location,
            "player_stats": {
                "wisdom": game_state.player.stats.wisdom,
                "strength": game_state.player.stats.strength,
                "karma": game_state.player.stats.karma,
                "mysticism": game_state.player.stats.mysticism,
                "charisma": game_state.player.stats.charisma,
            },
        }
        self.era_states[era] = era_data

    def get_era_state(self, era: TimeEra) -> Dict[str, Any]:
        """Get stored state for an era"""
        return self.era_states.get(era, {})

    def store_loop_memories(self, loop_number: int, game_state):
        """Store memories from a completed loop"""
        loop_data = {
            "decisions_made": game_state.decisions_made.copy(),
            "final_stats": {
                "wisdom": game_state.player.stats.wisdom,
                "strength": game_state.player.stats.strength,
                "karma": game_state.player.stats.karma,
                "mysticism": game_state.player.stats.mysticism,
                "charisma": game_state.player.stats.charisma,
            },
            "quests_completed": [],  # Would be populated by quest system
            "time_fragments_gained": game_state.time_fragments,
            "relationships": {},  # NPC relationship levels
        }
        self.loop_memories[loop_number] = loop_data

    def get_loop_memories(self) -> List[Dict[str, Any]]:
        """Get all stored loop memories"""
        return list(self.loop_memories.values())

    def store_npc_interaction(self, npc_id: str, interaction: Dict[str, Any]):
        """Store an interaction with an NPC"""
        if npc_id not in self.npc_memories:
            self.npc_memories[npc_id] = []

        self.npc_memories[npc_id].append(interaction)

    def get_npc_memories(self, npc_id: str) -> List[Dict[str, Any]]:
        """Get stored memories for a specific NPC"""
        return self.npc_memories.get(npc_id, [])

    def get_decisions_by_era(self, era: TimeEra) -> List[Dict[str, Any]]:
        """Get all decisions made in a specific era"""
        return [
            decision
            for decision in self.decision_memories
            if decision.get("era") == era
        ]

    def get_karma_affecting_decisions(self) -> List[Dict[str, Any]]:
        """Get decisions that affected karma"""
        return [
            decision
            for decision in self.decision_memories
            if "karma_impact" in decision and decision["karma_impact"] != 0
        ]

    def create_memory_summary(self) -> Dict[str, Any]:
        """Create a summary of all memories for narrative purposes"""
        return {
            "total_decisions": len(self.decision_memories),
            "loops_completed": len(self.loop_memories),
            "eras_visited": list(self.era_states.keys()),
            "important_events_count": len(self.important_events),
            "npcs_interacted": list(self.npc_memories.keys()),
            "karma_changes": len(self.get_karma_affecting_decisions()),
        }
