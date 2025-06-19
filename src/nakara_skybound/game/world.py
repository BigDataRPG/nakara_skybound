from dataclasses import dataclass, field
from typing import Any, Dict, List

from .character import NPC
from .time_system import TimeEra


@dataclass
class Location:
    id: str
    name: str
    description: str
    era_descriptions: Dict[TimeEra, str] = field(default_factory=dict)
    available_actions: List[str] = field(default_factory=list)
    connected_locations: List[str] = field(default_factory=list)
    npcs: List[str] = field(default_factory=list)  # NPC IDs
    special_properties: Dict[str, Any] = field(default_factory=dict)


class World:
    def __init__(self):
        self.locations: Dict[str, Location] = {}
        self.npcs: Dict[str, NPC] = {}
        self.current_era = TimeEra.PRESENT

    def initialize_locations(self):
        """Initialize all game locations"""
        # Central Plaza - Main hub
        self.locations["central_plaza"] = Location(
            id="central_plaza",
            name="จัตุรัสกลางเมือง",
            description="จุดศูนย์กลางของอัษฎานคร ที่ผู้คนมาพบปะกัน",
            era_descriptions={
                TimeEra.PAST: "จัตุรัสโบราณที่มีเจดีย์ทองคำสูงเสียดฟ้า ผู้คนสวมผ้าไหมมีลวดลาย",
                TimeEra.PRESENT: "จัตุรัสที่ผสมผสานระหว่างโบราณและสมัยใหม่ มีทั้งรถยนต์และรถม้า",
                TimeEra.FUTURE: "จัตุรัสที่เปลี่ยนไปตามการกระทำในอดีต อาจรุ่งเรืองหรือร้างผู้คน",
            },
            available_actions=["observe", "talk_to_people", "meditate", "time_travel"],
            connected_locations=["temple", "market", "library", "palace"],
            npcs=["sage_thewan", "merchant_niran"],
        )

        # Temple
        self.locations["temple"] = Location(
            id="temple",
            name="วัดพระแก้ว",
            description="วัดศักดิ์สิทธิ์ที่เป็นแหล่งเรียนรู้เวทมนตร์",
            era_descriptions={
                TimeEra.PAST: "วัดที่เต็มไปด้วยพระอาจารย์ผู้มีอิทธิฤทธิ์ มนต์เสียงดังก้องไปทั่ว",
                TimeEra.PRESENT: "วัดที่ยังคงมีพระสงฆ์ แต่การสอนเวทมนตร์เริ่มลดลง",
                TimeEra.FUTURE: "วัดที่อาจกลายเป็นซากปรักหักพัง หรือเป็นศูนย์กลางเวทมนตรคืนใหม่",
            },
            available_actions=[
                "pray",
                "learn_magic",
                "talk_to_people",
                "study_texts",
                "meditate",
            ],
            connected_locations=["central_plaza"],
            npcs=["monk_somdej", "apprentice_mali"],
            special_properties={"magic_learning": True, "karma_bonus": 1},
        )

        # Market
        self.locations["market"] = Location(
            id="market",
            name="ตลาดโบราณ",
            description="ตลาดคึกคักที่ขายสินค้าแปลกๆ จากทุกยุคสมัย",
            era_descriptions={
                TimeEra.PAST: "ตลาดที่ขายของมีเสน่ห์ เครื่องรางของขลัง และอัญมณีศักดิ์สิทธิ์",
                TimeEra.PRESENT: "ตลาดที่มีทั้งของโบราณและสมัยใหม่ ผู้คนหลากหลาย",
                TimeEra.FUTURE: "ตลาดที่เปลี่ยนไปตามโชคชะตาของเมือง",
            },
            available_actions=[
                "buy",
                "sell",
                "bargain",
                "gather_information",
                "observe",
            ],
            connected_locations=["central_plaza"],
            npcs=["trader_somchai", "fortune_teller_nim"],
        )

        # Library
        self.locations["library"] = Location(
            id="library",
            name="หอสมุดแห่งกาล",
            description="หอสมุดโบราณที่เก็บความรู้จากทุกยุคสมัย",
            era_descriptions={
                TimeEra.PAST: "หอสมุดที่เต็มไปด้วยใบลานและคัมภีร์โบราณ นักปราชญ์กำลังศึกษาเวทมนตร์",
                TimeEra.PRESENT: "หอสมุดที่มีทั้งหนังสือและเทคโนโลยีใหม่ ความรู้โบราณกำลังจะสูญหาย",
                TimeEra.FUTURE: "หอสมุดที่อาจเป็นแหล่งความรู้สุดท้าย หรือถูกทำลายไปแล้ว",
            },
            available_actions=[
                "research",
                "read_books",
                "study_history",
                "consult_librarian",
                "study_texts",
                "investigate",
                "meditate",
            ],
            connected_locations=["central_plaza"],
            npcs=["librarian_wichai"],
            special_properties={"wisdom_bonus": 2, "time_knowledge": True},
        )

        # Palace - Add this new location
        self.locations["palace"] = Location(
            id="palace",
            name="พระราชวัง",
            description="พระราชวังโบราณที่เป็นศูนย์กลางอำนาจและความลับ",
            era_descriptions={
                TimeEra.PAST: "พระราชวังอันงดงาม เต็มไปด้วยขุนนางและราชินี ความลับของอาณาจักรถูกซ่อนอยู่ที่นี่",
                TimeEra.PRESENT: "พระราชวังที่กลายเป็นพิพิธภัณฑ์ แต่ยังคงมีพลังลึกลับแฝงอยู่",
                TimeEra.FUTURE: "พระราชวังที่ผลของกรรมจะกำหนดว่าจะรุ่งเรืองหรือร้างผู้คน",
            },
            available_actions=[
                "explore_throne_room",
                "investigate_secrets",
                "talk_to_guards",
                "observe_artifacts",
                "meditate",
                "study_history",
            ],
            connected_locations=["central_plaza"],
            npcs=["royal_guard", "court_sage"],
            special_properties={"royal_secrets": True, "high_karma_required": True},
        )

    def populate_npcs(self):
        """Create and populate NPCs in the world"""
        # Sage in central plaza
        self.npcs["sage_thewan"] = NPC(
            id="sage_thewan",
            name="ปราชญ์เทวัญ",
            role="นักปราชญ์ผู้รู้เรื่องเวลา",
            location="central_plaza",
        )
        self.npcs["sage_thewan"].personality_traits = ["wise", "mysterious", "helpful"]
        self.npcs["sage_thewan"].available_quests = [
            "time_mystery",
            "ancient_knowledge",
        ]
        self.npcs["sage_thewan"].special_abilities = ["time_sight", "karma_reading"]

        # Merchant
        self.npcs["merchant_niran"] = NPC(
            id="merchant_niran",
            name="พ่อค้านิรันดร์",
            role="พ่อค้าของแปลก",
            location="central_plaza",
        )
        self.npcs["merchant_niran"].personality_traits = [
            "greedy",
            "cunning",
            "well_informed",
        ]
        self.npcs["merchant_niran"].available_quests = ["rare_items", "trading_network"]

        # Monk
        self.npcs["monk_somdej"] = NPC(
            id="monk_somdej",
            name="พระสมเด็จ",
            role="พระอาจารย์ผู้สอนเวทมนตร์",
            location="temple",
        )
        self.npcs["monk_somdej"].personality_traits = [
            "compassionate",
            "strict",
            "powerful",
        ]
        self.npcs["monk_somdej"].available_quests = [
            "meditation_mastery",
            "karma_cleansing",
        ]
        self.npcs["monk_somdej"].special_abilities = ["blessing", "karma_sight"]

        # Librarian
        self.npcs["librarian_wichai"] = NPC(
            id="librarian_wichai",
            name="บรรณารักษ์วิชัย",
            role="ผู้รักษาความรู้แห่งกาล",
            location="library",
        )
        self.npcs["librarian_wichai"].personality_traits = [
            "knowledgeable",
            "introverted",
            "meticulous",
        ]
        self.npcs["librarian_wichai"].available_quests = [
            "lost_knowledge",
            "time_records",
            "ancient_texts",
            "forbidden_books",
        ]
        self.npcs["librarian_wichai"].special_abilities = [
            "knowledge_keeper",
            "text_analysis",
        ]

        # Palace NPCs
        self.npcs["royal_guard"] = NPC(
            id="royal_guard",
            name="ทหารผู้พิทักษ์",
            role="ผู้คุ้มครองความลับของราชวัง",
            location="palace",
        )
        self.npcs["royal_guard"].personality_traits = [
            "loyal",
            "suspicious",
            "knowledgeable",
        ]
        self.npcs["royal_guard"].available_quests = [
            "royal_mystery",
            "ancient_artifact",
        ]

        self.npcs["court_sage"] = NPC(
            id="court_sage",
            name="ปราชญ์ราชสำนัก",
            role="นักปราชญ์ผู้รู้ความลับของกาลเวลา",
            location="palace",
        )
        self.npcs["court_sage"].personality_traits = ["wise", "secretive", "powerful"]
        self.npcs["court_sage"].available_quests = ["time_mastery", "royal_lineage"]
        self.npcs["court_sage"].special_abilities = ["time_reading", "prophecy"]

    def get_location(self, location_id: str) -> Location:
        """Get location by ID"""
        return self.locations.get(location_id)

    def get_npcs_in_location(self, location_id: str) -> List[NPC]:
        """Get all NPCs in a specific location"""
        location = self.get_location(location_id)
        if not location:
            return []

        return [self.npcs[npc_id] for npc_id in location.npcs if npc_id in self.npcs]

    def get_location_description(self, location_id: str, era: TimeEra) -> str:
        """Get era-specific description of a location"""
        location = self.get_location(location_id)
        if not location:
            return "ไม่พบสถานที่นี้"

        era_desc = location.era_descriptions.get(era)
        if era_desc:
            return f"{location.description}\n\n{era_desc}"
        return location.description

    def get_available_actions(self, location_id: str) -> List[str]:
        """Get available actions in a location"""
        location = self.get_location(location_id)
        return location.available_actions if location else []

    def update_npc_memories(self, loop_memories: List[Dict[str, Any]]):
        """Update NPC memories with loop information"""
        for npc in self.npcs.values():
            npc.update_memory_from_loop(loop_memories)

    def get_connected_locations(self, location_id: str) -> List[str]:
        """Get locations connected to current location"""
        location = self.get_location(location_id)
        return location.connected_locations if location else []
