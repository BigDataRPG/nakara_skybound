import json
import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

from .time_system import TimeEra


class NarrativeEngine:
    def __init__(self):
        # Initialize OpenAI client properly
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = OpenAI(api_key=api_key)
            self.openai_available = True
        else:
            self.client = None
            self.openai_available = False

        self.system_prompt = """
        คุณเป็น AI ที่สร้างเนื้อเรื่องสำหรับเกม RPG ไทย "ตำนานนครางกลับฟ้า: วัฏจักรกาล"
        
        เกมนี้มีธีม:
        - การเดินทางข้ามเวลา (อดีต ปัจจุบัน อนาคต)
        - วัฏจักรเวลา 7 วัน
        - เวทมนตร์และตำนานไทย
        - การตัดสินใจที่ส่งผลต่ออนาคต
        - NPC จดจำการกระทำจากรอบก่อน
        
        สร้างเนื้อเรื่องที่:
        - เป็นภาษาไทยที่สวยงาม
        - มีบรรยากาศลึกลับและตื่นเต้น
        - เชื่อมโยงกับเทพปกรณัมไทย
        - แสดงผลลัพธ์ของการตัดสินใจ
        - ให้ตัวเลือกที่มีความหมาย
        
        ตอบเป็น JSON เสมอ
        """

    def process_decision(self, decision: Dict[str, Any], game_state) -> Dict[str, Any]:
        """Process a player decision and generate narrative response"""

        # Handle basic actions with fallback narratives
        if decision["id"] == "general_action":
            return self._handle_basic_action(decision["choice"], game_state)

        # Try GPT first if available
        if self.openai_available:
            try:
                return self._generate_with_gpt(decision, game_state)
            except Exception as e:
                print(f"GPT Error: {e}")
                return self._get_fallback_narrative(decision, game_state)
        else:
            return self._get_fallback_narrative(decision, game_state)

    def _generate_with_gpt(
        self, decision: Dict[str, Any], game_state
    ) -> Dict[str, Any]:
        """Generate narrative using GPT with better blending"""
        prompt = f"""
        ผู้เล่นได้ตัดสินใจ: {decision['choice']}
        ในสถานการณ์: {decision['id']}
        ยุค: {decision['era'].value}
        สถานที่: {decision['location']}
        รอบที่: {decision['loop']}
        
        สถานะผู้เล่น:
        - ชื่อ: {game_state.player.name}
        - ปัญญา: {game_state.player.stats.wisdom}
        - กรรม: {game_state.player.stats.karma}
        - เศษเวลา: {game_state.time_fragments}
        - วันที่: {game_state.current_day}/7
        
        สร้างเรื่องเล่าในรูปแบบ JSON โดยในส่วน narrative ให้เป็นเรื่องเล่าที่ไหลลื่น 
        รวมผลลัพธ์เข้าไปในเนื้อเรื่องแทนที่จะแยกออกมา:
        
        {{
            "narrative": "เล่าเรื่องราวที่สมบูรณ์ รวมผลลัพธ์และความรู้สึกของตัวละครเข้าไปด้วย (ภาษาไทย)",
            "consequences": [
                {{"type": "stat_change", "stat": "karma", "value": 1}},
                {{"type": "day_advance", "amount": 1}}
            ],
            "next_options": [
                {{"id": "option1", "text": "ตัวเลือก 1"}},
                {{"id": "option2", "text": "ตัวเลือก 2"}}
            ]
        }}
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
            max_tokens=1200,
        )

        result = json.loads(response.choices[0].message.content)
        return result

    def _handle_basic_action(self, action: str, game_state) -> Dict[str, Any]:
        """Handle basic game actions with enhanced variety and day advancement"""

        # Location-specific actions
        location_actions = self._get_location_specific_actions(action, game_state)
        if location_actions:
            return location_actions

        # Era-specific content
        era_specific_content = {
            TimeEra.PAST: {
                "explore": {
                    "narrative": f"{game_state.player.name} สำรวจรอบๆ เมืองโบราณ... ผู้คนสวมชุดไทยประจำชาติ เสียงระฆังวัดดังไกล คุณเห็นนักเวทย์กำลังร่ายมนตร์อยู่ริมถนน และได้เรียนรู้เกี่ยวกับเวทมนตร์โบราณ วันหนึ่งผ่านไปอย่างมีความหมาย",
                    "consequences": [
                        {"type": "stat_change", "stat": "wisdom", "value": 2},
                        {"type": "stat_change", "stat": "mysticism", "value": 1},
                        {"type": "day_advance", "amount": 1},
                        {"type": "time_fragment", "amount": 1},
                    ],
                }
            },
            TimeEra.FUTURE: {
                "explore": {
                    "narrative": f"{game_state.player.name} สำรวจโลกอนาคต... เทคโนโลยีและเวทมนตร์ผสมผสานกัน คุณเห็นผลลัพธ์ของการกระทำในอดีต {'เมืองเจริญรุ่งเรืองเต็มไปด้วยความสุข' if game_state.player.stats.karma > 0 else 'เมืองร้างเปล่าและเต็มไปด้วยความเศร้า'} การสำรวจทำให้คุณเข้าใจถึงผลของกรรม",
                    "consequences": [
                        {"type": "stat_change", "stat": "wisdom", "value": 3},
                        {
                            "type": "stat_change",
                            "stat": "karma",
                            "value": 1 if game_state.player.stats.karma > 0 else -1,
                        },
                        {"type": "day_advance", "amount": 1},
                    ],
                }
            },
        }

        # Get era-specific content or fall back to present
        current_era_content = era_specific_content.get(game_state.current_era, {})
        if action in current_era_content:
            return current_era_content[action]

        # Default present-day actions with loop awareness
        loop_modifier = (
            ""
            if game_state.loop_count == 0
            else f" (รอบที่ {game_state.loop_count + 1}: คุณรู้สึกคุ้นเคยกับสถานที่นี้)"
        )

        action_responses = {
            "explore": {
                "narrative": f"{game_state.player.name} เดินสำรวจรอบๆ จัตุรัสกลางเมือง{loop_modifier}... ผู้คนต่างมองมาด้วยสายตาแปลกๆ บางคนเหมือนจะจำคุณได้ คุณพบร่องรอยเวทมนตร์โบราณ และได้พบกับนักเดินทางคนอื่นๆ วันหนึ่งผ่านไปอย่างมีความหมาย",
                "consequences": [
                    {"type": "stat_change", "stat": "wisdom", "value": 1},
                    {"type": "day_advance", "amount": 1},
                    {
                        "type": "item_gain",
                        "item": {
                            "id": "clue1",
                            "name": "เบาะแสลึกลับ",
                            "description": "ข้อมูลที่อาจมีประโยชน์",
                            "type": "information",
                            "power": 0,
                            "magical_properties": {},
                        },
                    },
                ],
                "next_options": [
                    {"id": "continue_explore", "text": "สำรวจลึกขึ้น"},
                    {"id": "talk_to_people", "text": "เข้าไปคุยกับใครสักคน"},
                    {"id": "meditate", "text": "นั่งสมาธิเพื่อใคร่ครวญ"},
                ],
            },
            # ...existing actions...
        }

        return action_responses.get(
            action, self._get_fallback_narrative({"choice": action}, game_state)
        )

    def _get_fallback_narrative(
        self, decision: Dict[str, Any], game_state
    ) -> Dict[str, Any]:
        """Generate fallback narrative when specific action is not found"""
        action_choice = decision.get("choice", "การกระทำ")

        return {
            "narrative": f"คุณได้ตัดสินใจ {action_choice} ผลลัพธ์ของการกระทำนี้จะปรากฏในอนาคต... ความลึกลับของเวลายังคงปิดบังอยู่ วันหนึ่งผ่านไปอย่างรวดเร็ว",
            "consequences": [
                {"type": "stat_change", "stat": "wisdom", "value": 1},
                {"type": "day_advance", "amount": 1},
            ],
            "next_options": [
                {"id": "explore", "text": "สำรวจต่อไป"},
                {"id": "talk_to_people", "text": "คุยกับผู้คน"},
                {"id": "meditate", "text": "ทำสมาธิ"},
            ],
        }

    def _get_location_specific_actions(self, action: str, game_state) -> Dict[str, Any]:
        """Handle location-specific actions"""
        location = game_state.current_location

        # Palace actions
        if location == "palace":
            palace_actions = {
                "explore_throne_room": {
                    "narrative": f"{game_state.player.name} เข้าไปในห้องบัลลังก์... บัลลังก์ทองคำเก่าแก่ปรากฏอยู่ตรงหน้า คุณรู้สึกถึงพลังลึกลับที่แฝงอยู่ ภาพนิมิตของกษัตริย์ในอดีตปรากฏขึ้นในจิตใจ",
                    "consequences": [
                        {"type": "stat_change", "stat": "mysticism", "value": 2},
                        {"type": "stat_change", "stat": "wisdom", "value": 1},
                        {"type": "day_advance", "amount": 1},
                        {"type": "quest_start", "quest_name": "ความลับของบัลลังก์"},
                    ],
                },
                "investigate_secrets": {
                    "narrative": f"{game_state.player.name} ค้นหาความลับในพระราชวัง... คุณพบห้องลับที่เต็มไปด้วยเอกสารโบราณ ความจริงเกี่ยวกับวัฏจักรเวลาเริ่มเผยออกมา",
                    "consequences": [
                        {"type": "stat_change", "stat": "wisdom", "value": 3},
                        {"type": "time_fragment", "amount": 2},
                        {"type": "day_advance", "amount": 1},
                    ],
                },
            }
            if action in palace_actions:
                return palace_actions[action]

        # Library actions
        elif location == "library":
            library_actions = {
                "research": {
                    "narrative": f"{game_state.player.name} ใช้เวลาค้นคว้าในหอสมุด... คุณพบตำราโบราณที่บันทึกเรื่องการเดินทางข้ามเวลา ความรู้ใหม่ๆ เข้ามาในหัว",
                    "consequences": [
                        {"type": "stat_change", "stat": "wisdom", "value": 2},
                        {"type": "stat_change", "stat": "mysticism", "value": 1},
                        {"type": "time_fragment", "amount": 1},
                        {"type": "day_advance", "amount": 1},
                    ],
                },
                "read_books": {
                    "narrative": f"{game_state.player.name} อ่านหนังสือในหอสมุด... เรื่องราวของอดีตและอนาคตปรากฏในหน้ากระดาษ คุณเข้าใจถึงรูปแบบของวัฏจักรเวลามากขึ้น",
                    "consequences": [
                        {"type": "stat_change", "stat": "wisdom", "value": 1},
                        {"type": "stat_change", "stat": "mysticism", "value": 1},
                    ],
                },
                "consult_librarian": {
                    "narrative": f"{game_state.player.name} ปรึกษาบรรณารักษ์... เขาให้ข้อมูลที่มีค่าเกี่ยวกับการควบคุมเวลา และมอบหนังสือลับให้คุณ",
                    "consequences": [
                        {"type": "stat_change", "stat": "wisdom", "value": 2},
                        {
                            "type": "item_gain",
                            "item": {
                                "id": "secret_book",
                                "name": "คัมภีร์ลับแห่งกาล",
                                "description": "หนังสือที่เผยความลับของเวลา",
                                "type": "magical",
                                "power": 5,
                                "magical_properties": {"time_knowledge": True},
                            },
                        },
                        {"type": "day_advance", "amount": 1},
                    ],
                },
            }
            if action in library_actions:
                return library_actions[action]

        return None

    def generate_time_travel_scene(
        self, from_era: TimeEra, to_era: TimeEra, game_state
    ) -> str:
        """Generate narrative for time travel scenes with seamless storytelling"""

        if self.openai_available:
            try:
                prompt = f"""
                สร้างเรื่องเล่าการเดินทางข้ามเวลาจาก{from_era.value}ไปยัง{to_era.value}
                
                ผู้เล่น: {game_state.player.name}
                กรรมปัจจุบัน: {game_state.player.stats.karma}
                
                เล่าเป็นเรื่องราวที่ไหลลื่น อธิบาย:
                - ความรู้สึกขณะเดินทางข้ามเวลา
                - การเปลี่ยนแปลงของสภาพแวดล้อม
                - ผลของกรรมที่มีต่อการเดินทาง
                - บรรยากาศและความรู้สึกของตัวละคร
                
                ความยาว 3-4 ประโยค ภาษาไทยที่สวยงาม
                """

                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.9,
                    max_tokens=600,
                )

                return response.choices[0].message.content

            except Exception as e:
                print(f"GPT Error in time travel: {e}")

        # Enhanced fallback with karma consideration
        karma_effect = ""
        if game_state.player.stats.karma > 10:
            karma_effect = "แสงทองอ่อนโยนล้อมรอบคุณ เป็นสัญญาณของกรรมดีที่ปกป้อง"
        elif game_state.player.stats.karma < -10:
            karma_effect = "เงามืดปกคลุมการเดินทาง เป็นภาพสะท้อนของกรรมลบที่ติดตาม"
        else:
            karma_effect = "แสงและเงาผสมผสาน สะท้อนความสมดุลในจิตใจ"

        return f"""คุณรู้สึกเวลาเบิ่งบานรอบตัว ความเป็นจริงละลายและปรับรูปร่างใหม่ {karma_effect} เสียงลมหวือในห้วงเวลาก้องกังวาน และทุกอย่างเปลี่ยนแปลงอย่างน่าอัศจรรย์ เมื่อความชัดเจนกลับคืนมา คุณพบว่าตัวเองมาถึง{to_era.value}แล้ว โลกใหม่กินบนรากฐานของการกระทำในอดีต"""

    def generate_loop_reset_scene(self, loop_count: int, game_state) -> str:
        """Generate narrative for time loop reset with seamless storytelling"""

        previous_karma = game_state.player.stats.karma
        decisions_count = len(game_state.decisions_made)

        if self.openai_available:
            try:
                prompt = f"""
                สร้างเรื่องเล่าการรีเซ็ตวัฏจักรเวลาครั้งที่ {loop_count}
                
                ข้อมูลจากรอบก่อน:
                - การตัดสินใจ: {decisions_count} ครั้ง
                - กรรมสุดท้าย: {previous_karma}
                - เศษเวลา: {game_state.time_fragments}
                
                เล่าเป็นเรื่องราวที่สมบูรณ์ ครอบคลุม:
                - ความรู้สึกของการกลับมาใหม่
                - การเปลี่ยนแปลงของโลกตามกรรม
                - ปฏิกิริยาของ NPC ที่จำได้
                - ความหวังหรือความกังวลสำหรับรอบใหม่
                
                ความยาว 4-5 ประโยค ภาษาไทยที่ไหลลื่น
                """

                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.8,
                    max_tokens=800,
                )

                return response.choices[0].message.content

            except Exception as e:
                print(f"GPT Error in loop reset: {e}")

        # Enhanced fallback with flowing narrative
        karma_effect = ""
        world_change = ""

        if previous_karma > 10:
            karma_effect = "ผู้คนในจัตุรัสส่งยิ้มอบอุ่นมาให้คุณ"
            world_change = "ดวงอาทิตย์ส่องแสงสดใสขึ้น และสายลมหอบเอาความหวังมาสู่ใจ"
        elif previous_karma < -10:
            karma_effect = "ผู้คนหลีกเลี่ยงสายตาคุณด้วยความระแวง"
            world_change = "เมฆมืดปกคลุมท้องฟ้า และอากาศเหนียวหนืดด้วยความไม่สงบ"
        else:
            karma_effect = "ผู้คนมองคุณด้วยความอยากรู้ผสมความระมัดระวัง"
            world_change = "ท้องฟ้าครึ่งแสงครึ่งเงา สะท้อนความไม่แน่นอนของอนาคต"

        return f"""เวลาหมุนกลับสู่จุดเริ่มต้นอีกครั้ง และรอบที่ {loop_count} ได้เริ่มต้นขึ้นแล้ว แต่ครั้งนี้โลกต่างออกไป {world_change} {karma_effect} บางคนเหลือบมองคุณด้วยประกายแห่งการจดจำ ราวกับว่าความทรงจำจากรอบก่อนยังคงหลงเหลืออยู่ คุณรู้ดีว่าการตัดสินใจ {decisions_count} ครั้งในอดีตได้สร้างร่องรอยที่ไม่อาจลบเลือน และในรอบนี้ ทุกการกระทำจะมีความหมายมากยิ่งขึ้น"""
