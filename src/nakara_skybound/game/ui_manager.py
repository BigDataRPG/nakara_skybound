from typing import Any, Dict, List

import streamlit as st

from .character import CharacterClass, Player
from .game_engine import GameEngine, GameState
from .time_system import TimeEra


class UIManager:
    def __init__(self):
        self.current_scene = None

    def render_game_state(self, state: GameState):
        """Render the current game state UI"""
        # Handle user input first to avoid loops
        self._handle_pending_actions(state)

        # Sidebar with player info
        self._render_sidebar(state)

        # Main game area
        col1, col2 = st.columns([2, 1])

        with col1:
            self._render_main_scene(state)

        with col2:
            self._render_info_panel(state)

    def _handle_pending_actions(self, state: GameState):
        """Handle pending actions without causing infinite loops"""
        # Handle character creation completion
        if (
            hasattr(st.session_state, "should_update_character")
            and st.session_state.should_update_character
        ):
            # Update player info
            state.player.name = st.session_state.player_name
            state.player.character_class = CharacterClass(st.session_state.player_class)

            # Reset stats based on new class
            state.player._set_class_stats()

            # Change scene to post-creation
            state.current_scene = "character_created"

            # Give starting time fragments
            state.time_fragments = 2

            # Clear the flag
            st.session_state.should_update_character = False
            st.session_state.character_created = True

    def _render_sidebar(self, state: GameState):
        """Render player information sidebar"""
        with st.sidebar:
            st.header(f"🧙‍♂️ {state.player.name}")
            st.subheader(f"นัก{state.player.character_class.value}")

            # Era and location indicator with more detailed info
            era_info = {
                TimeEra.PAST: ("🏛️", "อดีตกาล", "ยุคทองของอัษฎานคร"),
                TimeEra.PRESENT: ("🏙️", "ปัจจุบันกาล", "ยุคแห่งการเปลี่ยนแปลง"),
                TimeEra.FUTURE: ("🌆", "อนาคตกาล", "ยุคแห่งผลลัพธ์"),
            }
            era_icon, era_name, era_desc = era_info.get(
                state.current_era, ("❓", "ไม่ทราบ", "")
            )
            st.write(f"**ยุค:** {era_icon} {era_name}")
            if era_desc:
                st.caption(era_desc)

            # Location with Thai names
            location_names = {
                "central_plaza": "จัตุรัสกลางเมือง",
                "temple": "วัดพระแก้ว",
                "market": "ตลาดโบราณ",
                "library": "หอสมุดแห่งกาล",
                "palace": "พระราชวัง",
            }
            current_location_thai = location_names.get(
                state.current_location, state.current_location
            )
            st.write(f"**สถานที่:** 📍 {current_location_thai}")

            # Player stats with more visual feedback
            st.subheader("📊 สถานะ")
            stats = state.player.stats

            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "ปัญญา",
                    stats.wisdom,
                    delta=(
                        None
                        if not hasattr(st.session_state, "last_wisdom")
                        else stats.wisdom
                        - st.session_state.get("last_wisdom", stats.wisdom)
                    ),
                )
                st.metric(
                    "กำลัง",
                    stats.strength,
                    delta=(
                        None
                        if not hasattr(st.session_state, "last_strength")
                        else stats.strength
                        - st.session_state.get("last_strength", stats.strength)
                    ),
                )
                st.metric(
                    "เวทมนตร์",
                    stats.mysticism,
                    delta=(
                        None
                        if not hasattr(st.session_state, "last_mysticism")
                        else stats.mysticism
                        - st.session_state.get("last_mysticism", stats.mysticism)
                    ),
                )

            with col2:
                st.metric(
                    "เสน่ห์",
                    stats.charisma,
                    delta=(
                        None
                        if not hasattr(st.session_state, "last_charisma")
                        else stats.charisma
                        - st.session_state.get("last_charisma", stats.charisma)
                    ),
                )
                st.metric(
                    "กรรม",
                    stats.karma,
                    delta=(
                        None
                        if not hasattr(st.session_state, "last_karma")
                        else stats.karma
                        - st.session_state.get("last_karma", stats.karma)
                    ),
                )
                st.metric(
                    "เศษเวลา",
                    state.time_fragments,
                    delta=(
                        None
                        if not hasattr(st.session_state, "last_fragments")
                        else state.time_fragments
                        - st.session_state.get("last_fragments", state.time_fragments)
                    ),
                )

            # Store current stats for next comparison
            st.session_state.last_wisdom = stats.wisdom
            st.session_state.last_strength = stats.strength
            st.session_state.last_mysticism = stats.mysticism
            st.session_state.last_charisma = stats.charisma
            st.session_state.last_karma = stats.karma
            st.session_state.last_fragments = state.time_fragments

            # Day and loop counter with progress visualization
            day_progress = state.current_day / 7
            st.write(f"**วันที่:** {state.current_day}/7")
            st.progress(day_progress, text=f"ความคืบหนาในวัฏจักร")
            st.write(f"**รอบที่:** {state.loop_count + 1}")

            # Show inventory if player has items
            if state.player.inventory:
                st.subheader("🎒 สิ่งของ")
                for item in state.player.inventory[:3]:  # Show first 3 items
                    # Handle both Item objects and dictionaries
                    if hasattr(item, "name"):
                        item_name = item.name
                    elif isinstance(item, dict):
                        item_name = item.get("name", "ไม่ทราบชื่อ")
                    else:
                        item_name = str(item)
                    st.write(f"• {item_name}")
                if len(state.player.inventory) > 3:
                    st.caption(f"และอีก {len(state.player.inventory) - 3} รายการ...")

    def _render_main_scene(self, state: GameState):
        """Render the main game scene"""
        # Display location with era-specific styling
        location_names = {
            "central_plaza": "จัตุรัสกลางเมือง",
            "temple": "วัดพระแก้ว",
            "market": "ตลาดโบราณ",
            "library": "หอสมุดแห่งกาล",
            "palace": "พระราชวัง",
        }
        current_location_thai = location_names.get(
            state.current_location, state.current_location
        )

        # Era-specific styling
        if state.current_era == TimeEra.PAST:
            st.markdown(f"### 🏛️ {current_location_thai} - {state.current_era.value}")
        elif state.current_era == TimeEra.FUTURE:
            st.markdown(f"### 🌆 {current_location_thai} - {state.current_era.value}")
        else:
            st.markdown(f"### 🏙️ {current_location_thai} - {state.current_era.value}")

        # Display any recent action results
        if (
            hasattr(st.session_state, "last_action_result")
            and st.session_state.last_action_result
        ):
            self._display_action_result(st.session_state.last_action_result)
            st.divider()

        # Scene description
        if state.current_scene == "game_start":
            self._render_intro_scene(state)
        elif state.current_scene == "character_created":
            self._render_post_creation_scene(state)
        elif state.current_scene == "action_result":
            self._render_action_result_scene(state)
        elif state.current_scene == "loop_reset":
            self._render_loop_reset_scene(state)
        else:
            self._render_standard_scene(state)

    def _display_action_result(self, result: Dict[str, Any]):
        """Display the result of an action as flowing narrative"""
        # Create a complete narrative story
        narrative_parts = []

        if "narrative" in result:
            narrative_parts.append(result["narrative"])

        # Blend consequences into the narrative
        if "consequences" in result and result["consequences"]:
            consequence_text = []
            for consequence in result["consequences"]:
                if consequence["type"] == "stat_change":
                    stat_name = {
                        "wisdom": "ปัญญา",
                        "strength": "กำลัง",
                        "mysticism": "เวทมนตร์",
                        "charisma": "เสน่ห์",
                        "karma": "กรรม",
                    }.get(consequence["stat"], consequence["stat"])

                    value = consequence["value"]
                    if value > 0:
                        consequence_text.append(f"{stat_name}ของคุณเพิ่มขึ้น")
                    else:
                        consequence_text.append(f"{stat_name}ของคุณลดลง")

                elif consequence["type"] == "time_fragment":
                    amount = consequence["amount"]
                    consequence_text.append(f"คุณได้รับเศษเวลา {amount} ชิ้น")

                elif consequence["type"] == "item_gain":
                    item = consequence["item"]
                    consequence_text.append(f"คุณได้รับ '{item['name']}'")

                elif consequence["type"] == "day_advance":
                    days = consequence["amount"]
                    if days == 1:
                        consequence_text.append("วันหนึ่งผ่านไปอย่างรวดเร็ว")
                    else:
                        consequence_text.append(f"เวลาผ่านไป {days} วัน")

                elif consequence["type"] == "quest_start":
                    quest_name = consequence["quest_name"]
                    consequence_text.append(f"ภารกิจใหม่เริ่มต้นขึ้น: '{quest_name}'")

                elif consequence["type"] == "relationship_change":
                    npc_name = consequence["npc_name"]
                    change = consequence["change"]
                    if change > 0:
                        consequence_text.append(f"ความสัมพันธ์กับ{npc_name}ดีขึ้น")
                    else:
                        consequence_text.append(f"ความสัมพันธ์กับ{npc_name}แย่ลง")

            # Blend consequences into narrative
            if consequence_text:
                if len(consequence_text) == 1:
                    narrative_parts.append(f"\n\n{consequence_text[0]}")
                elif len(consequence_text) == 2:
                    narrative_parts.append(
                        f"\n\n{consequence_text[0]} และ{consequence_text[1]}"
                    )
                else:
                    consequence_sentence = (
                        ", ".join(consequence_text[:-1]) + f" และ{consequence_text[-1]}"
                    )
                    narrative_parts.append(f"\n\n{consequence_sentence}")

        # Display as a single flowing narrative
        complete_narrative = "".join(narrative_parts)

        # Use a nice container for the story
        with st.container():
            st.markdown("### 📖 เรื่องราว")
            st.markdown(f"*{complete_narrative}*")

    def _render_standard_scene(self, state: GameState):
        """Render a standard game scene with enhanced actions"""
        # Get location description from world
        from .world import World

        world = World()
        world.initialize_locations()

        location_desc = world.get_location_description(
            state.current_location, state.current_era
        )
        st.write(location_desc)

        # Enhanced available actions with variety
        available_actions = world.get_available_actions(state.current_location)
        if available_actions:
            st.subheader("🎯 การกระทำที่สามารถทำได้:")

            # Group actions by type for better organization
            exploration_actions = [
                a
                for a in available_actions
                if a in ["observe", "explore", "investigate"]
            ]
            social_actions = [
                a
                for a in available_actions
                if a in ["talk_to_people", "gossip", "negotiate"]
            ]
            spiritual_actions = [
                a for a in available_actions if a in ["meditate", "pray", "study_texts"]
            ]
            other_actions = [
                a
                for a in available_actions
                if a not in exploration_actions + social_actions + spiritual_actions
            ]

            if exploration_actions:
                st.write("**🔍 การสำรวจ:**")
                cols = st.columns(len(exploration_actions))
                for i, action in enumerate(exploration_actions):
                    with cols[i]:
                        action_names = {
                            "observe": "สังเกตการณ์",
                            "explore": "สำรวจ",
                            "investigate": "ตรวจสอบ",
                        }
                        if st.button(
                            action_names.get(action, action),
                            key=f"explore_{action}_{i}",
                        ):
                            st.session_state.action_taken = action
                            st.session_state.action_category = "exploration"

            if social_actions:
                st.write("**💬 การสื่อสาร:**")
                cols = st.columns(len(social_actions))
                for i, action in enumerate(social_actions):
                    with cols[i]:
                        action_names = {
                            "talk_to_people": "คุยกับคน",
                            "gossip": "ฟังข่าวลือ",
                            "negotiate": "เจรจา",
                        }
                        if st.button(
                            action_names.get(action, action), key=f"social_{action}_{i}"
                        ):
                            st.session_state.action_taken = action
                            st.session_state.action_category = "social"

            if spiritual_actions:
                st.write("**🧘 การปฏิบัติธรรม:**")
                cols = st.columns(len(spiritual_actions))
                for i, action in enumerate(spiritual_actions):
                    with cols[i]:
                        action_names = {
                            "meditate": "ทำสมาธิ",
                            "pray": "สวดมนตร์",
                            "study_texts": "ศึกษาคัมภีร์",
                        }
                        if st.button(
                            action_names.get(action, action),
                            key=f"spiritual_{action}_{i}",
                        ):
                            st.session_state.action_taken = action
                            st.session_state.action_category = "spiritual"

        # Show NPCs with interaction options
        npcs = world.get_npcs_in_location(state.current_location)
        if npcs:
            st.subheader("👥 บุคคลในบริเวณนี้:")
            for npc in npcs:
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"• **{npc.name}** - {npc.role}")
                with col2:
                    if st.button(f"คุย", key=f"talk_to_{npc.id}"):
                        st.session_state.action_taken = f"talk_to_{npc.id}"
                        st.session_state.action_category = "npc_interaction"

    def _render_info_panel(self, state: GameState):
        """Render information panel with all locations available"""
        st.subheader("📋 ข้อมูล")

        # Show current day progress with warning as it approaches 7
        progress = state.current_day / 7
        if state.current_day >= 6:
            st.warning(f"⚠️ เหลือเวลาอีกเพียง {7 - state.current_day} วัน!")
        st.progress(progress, text=f"วันที่ {state.current_day}/7 ในวัฏจักร")

        # Active quests
        if state.active_quests:
            st.write("**ภารกิจที่กำลังดำเนินการ:**")
            for quest in state.active_quests:
                st.write(f"• {quest}")

        # Location movement - can travel to ANY location, not just connected ones
        st.subheader("🗺️ การเดินทาง")
        all_locations = {
            "central_plaza": "จัตุรัสกลางเมือง",
            "temple": "วัดพระแก้ว",
            "market": "ตลาดโบราณ",
            "library": "หอสมุดแห่งกาล",
            "palace": "พระราชวัง",
        }

        current_location_thai = all_locations.get(
            state.current_location, state.current_location
        )
        st.write(f"**ตำแหน่งปัจจุบัน:** {current_location_thai}")

        # Show all available locations except current one
        available_locations = {
            k: v for k, v in all_locations.items() if k != state.current_location
        }

        selected_location = st.selectbox(
            "เลือกสถานที่ที่ต้องการไป:",
            options=list(available_locations.keys()),
            format_func=lambda x: available_locations[x],
            key="location_travel_select",
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚶 ไปเลย", key="instant_travel"):
                st.session_state.new_location = selected_location
        with col2:
            # Time cost for travel (advances day)
            if st.button("🏃 ไปอย่างรวดเร็ว", key="fast_travel"):
                st.session_state.new_location = selected_location
                st.session_state.advance_day = True

        # Time travel options
        st.subheader("⏰ การเดินทางข้ามเวลา")

        # Check requirements and show them
        if state.time_fragments < 3:
            st.write("🏛️ เดินทางสู่อดีต")
            st.caption(f"ต้องการเศษเวลา 3 ชิ้น (คุณมี {state.time_fragments} ชิ้น)")
        else:
            if st.button("🏛️ เดินทางสู่อดีต", key="travel_past"):
                st.session_state.pending_time_travel = TimeEra.PAST

        if state.time_fragments < 5:
            st.write("🌆 เดินทางสู่อนาคต")
            st.caption(f"ต้องการเศษเวลา 5 ชิ้น (คุณมี {state.time_fragments} ชิ้น)")
        else:
            if st.button("🌆 เดินทางสู่อนาคต", key="travel_future"):
                st.session_state.pending_time_travel = TimeEra.FUTURE

        if state.current_era != TimeEra.PRESENT:
            if st.button("🏙️ กลับสู่ปัจจุบัน", key="travel_present"):
                st.session_state.pending_time_travel = TimeEra.PRESENT

        # Loop control with story completion check
        st.subheader("🔄 วัฏจักรเวลา")
        if state.current_day >= 7:
            st.error("🎭 **เรื่องราวใกล้จบแล้ว!** 7 วันครบแล้ว!")
            st.write("คุณได้เรียนรู้อะไรบ้างในวัฏจักรนี้?")
            if st.button("📖 ดูบทสรุป", key="view_summary"):
                st.session_state.show_summary = True
            if st.button("🔄 เริ่มวัฏจักรใหม่", key="trigger_loop"):
                st.session_state.trigger_loop = True
        else:
            st.info(f"เหลืออีก {7 - state.current_day} วัน ก่อนวัฏจักรจะสิ้นสุด")
            # Show what will happen when cycle completes
            st.caption("เมื่อครบ 7 วัน คุณจะได้เห็นผลลัพธ์ของการกระทำทั้งหมด")

        # Show summary if requested
        if hasattr(st.session_state, "show_summary") and st.session_state.show_summary:
            self._show_cycle_summary(state)

    def _show_cycle_summary(self, state: GameState):
        """Show summary of the current cycle"""
        st.subheader("📜 บทสรุปวัฏจักรนี้")

        # Create narrative summary instead of data tables
        karma = state.player.stats.karma
        decisions_count = len(state.decisions_made)
        days_used = state.current_day if state.current_day <= 7 else 7

        # Build narrative summary
        summary_parts = []

        # Opening
        summary_parts.append(
            f"ในวัฏจักรที่ผ่านไป คุณได้ใช้เวลา {days_used} วัน และตัดสินใจสำคัญไป {decisions_count} ครั้ง"
        )

        # Karma assessment with narrative
        if karma > 15:
            summary_parts.append(
                "การกระทำของคุณได้สร้างกรรมดีอย่างล้นเหลือ ดวงวิญญาณของคุณเปล่งประกายด้วยความบริสุทธิ์"
            )
        elif karma > 10:
            summary_parts.append("คุณได้สร้างกรรมดีไว้มากมาย ผู้คนจะจดจำความเมตตาของคุณ")
        elif karma > 0:
            summary_parts.append("คุณมีกรรมดีเล็กน้อย แต่ยังมีที่ให้ปรับปรุง")
        elif karma == 0:
            summary_parts.append("คุณรักษาสมดุลระหว่างดีและชั่วไว้ได้ ทางกลางคือภูมิปัญญา")
        elif karma > -10:
            summary_parts.append("คุณมีกรรมลบเล็กน้อย แต่ยังมีโอกาสแก้ไข")
        else:
            summary_parts.append("การกระทำของคุณได้สร้างกรรมลบไว้มาก เงาของความผิดติดตามคุณไป")

        # Time fragments and wisdom
        if state.time_fragments > 5:
            summary_parts.append(
                f"คุณรวบรวมเศษเวลาได้ {state.time_fragments} ชิ้น ซึ่งแสดงถึงความเข้าใจในธรรมชาติของเวลา"
            )

        if state.player.stats.wisdom > 20:
            summary_parts.append("ปัญญาของคุณได้เติบโตจนกลายเป็นปราชญ์ผู้ยิ่งใหญ่")
        elif state.player.stats.wisdom > 15:
            summary_parts.append("ปัญญาของคุณเติบโตขึ้นอย่างน่าประทับใจ")

        # Quests
        if state.active_quests:
            if len(state.active_quests) == 1:
                summary_parts.append(
                    f"คุณยังคงมีภารกิจ '{state.active_quests[0]}' ที่ต้องดำเนินการต่อ"
                )
            else:
                summary_parts.append(
                    f"คุณมีภารกิจ {len(state.active_quests)} อย่างที่รอการดำเนินการ"
                )

        # Future prediction
        if karma > 5:
            summary_parts.append(
                "\n\nในวัฏจักรหน้า ผู้คนจะต้อนรับคุณด้วยรอยยิ้ม และเปิดใจให้ความช่วยเหลือ กรรมดีที่คุณสั่งสมจะเป็นแสงนำทางในความมืด"
            )
        elif karma < -5:
            summary_parts.append(
                "\n\nในวัฏจักรหน้า ผู้คนจะหลีกเลี่ยงสายตาคุณ ความไม่ไว้วางใจจะเป็นเงาที่ตามติด แต่ยังมีโอกาสที่จะแก้ไขกรรมลบ"
            )
        else:
            summary_parts.append(
                "\n\nในวัฏจักรหน้า ทุกอย่างยังเป็นไปได้ ชะตากรรมยังไม่ถูกกำหนด และคุณยังมีอำนาจที่จะเปลี่ยนแปลงอนาคต"
            )

        # Display as flowing narrative
        complete_summary = " ".join(summary_parts)

        with st.container():
            st.markdown(f"*{complete_summary}*")

        # Simple stats for reference
        with st.expander("📊 ดูรายละเอียดเพิ่มเติม"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("การตัดสินใจ", decisions_count)
                st.metric("วันที่ใช้", days_used)
            with col2:
                st.metric("กรรม", karma)
                st.metric("ปัญญา", state.player.stats.wisdom)
            with col3:
                st.metric("เศษเวลา", state.time_fragments)
                st.metric("ภารกิจ", len(state.active_quests))

    def _render_intro_scene(self, state: GameState):
        """Render the game introduction scene"""
        st.markdown(
            """
        ### 🌅 จุดเริ่มต้นแห่งตำนาน
        
        คุณตื่นขึ้นมาที่จัตุรัสกลางเมืองอัษฎานคร ความทรงจำเลื่อนลอย...
        
        *"เวลา...ไม่ใช่แค่สิ่งที่ผ่านไป แต่มันย้อนกลับมา…ทวงสิ่งที่เราทำไว้"*
        
        เสียงแปลกๆ ก้องอยู่ในหัว และคุณรู้สึกว่าเรื่องราวนี้...เคยเกิดขึ้นมาก่อน
        """
        )

        # Character creation if first time
        if (
            not hasattr(st.session_state, "character_created")
            or not st.session_state.character_created
        ):
            self._render_character_creation()

    def _render_character_creation(self):
        """Render character creation interface"""
        st.subheader("🎭 สร้างตัวละคร")

        # Initialize form data in session state if not exists
        if "form_name" not in st.session_state:
            st.session_state.form_name = "ผู้เดินทาง"
        if "form_class" not in st.session_state:
            st.session_state.form_class = "sage"

        name = st.text_input(
            "ชื่อของคุณ:", value=st.session_state.form_name, key="character_name_input"
        )

        character_class = st.selectbox(
            "เลือกเส้นทางของคุณ:",
            options=["sage", "warrior", "mystic"],
            index=["sage", "warrior", "mystic"].index(st.session_state.form_class),
            format_func=lambda x: {
                "sage": "🧙‍♂️ นักปราชญ์ - เชี่ยวชาญเรื่องปัญญาและเวทมนตร์",
                "warrior": "⚔️ นักรบ - เชี่ยวชาญเรื่องการต่อสู้และเสน่ห์",
                "mystic": "🔮 นักเวทย์ - เชี่ยวชาญเรื่องเวทมนตร์และปัญญา",
            }[x],
            key="character_class_select",
        )

        # Update session state
        st.session_state.form_name = name
        st.session_state.form_class = character_class

        if st.button("เริ่มการเดินทาง", key="start_journey_btn"):
            # Store character creation data
            st.session_state.player_name = name
            st.session_state.player_class = character_class
            st.session_state.should_update_character = True
            # Don't call st.rerun() here - let the next render cycle handle it

    def _render_post_creation_scene(self, state: GameState):
        """Render scene after character creation"""
        st.markdown(
            f"""
        ### 🌟 ยินดีต้อนรับ {state.player.name}
        
        ตัวตนของคุณเริ่มชัดเจนขึ้น... คุณคือ{state.player.character_class.value}ผู้มีพลังพิเศษ
        
        รอบๆ ตัวคุณมีผู้คนมากมาย บางคนมองคุณด้วยสายตาแปลกๆ
        เหมือนกับว่าพวกเขารู้จักคุณมาก่อน...
        
        ### 🎯 สิ่งที่คุณสามารถทำได้:
        """
        )

        # Show available actions
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔍 สำรวจรอบๆ", key="explore_btn"):
                st.session_state.action_taken = "explore"

        with col2:
            if st.button("💬 คุยกับคนใกล้ๆ", key="talk_btn"):
                st.session_state.action_taken = "talk"

        with col3:
            if st.button("🧘 ทำสมาธิ", key="meditate_btn"):
                st.session_state.action_taken = "meditate"

    def _render_action_result_scene(self, state: GameState):
        """Render scene after an action has been taken"""
        # Get the last action result
        last_result = getattr(st.session_state, "last_action_result", {})

        if last_result and "next_options" in last_result:
            st.subheader("🎯 ตัวเลือกถัดไป:")

            # Display next options as buttons
            cols = st.columns(min(len(last_result["next_options"]), 3))
            for i, option in enumerate(last_result["next_options"]):
                with cols[i % 3]:
                    if st.button(option["text"], key=f"next_option_{option['id']}_{i}"):
                        st.session_state.action_taken = option["id"]
        else:
            # Default continuing options
            st.subheader("🎯 ตัวเลือกถัดไป:")
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("🔍 สำรวจต่อไป", key="continue_explore"):
                    st.session_state.action_taken = "explore"

            with col2:
                if st.button("💬 คุยกับคนอื่น", key="continue_talk"):
                    st.session_state.action_taken = "talk"

            with col3:
                if st.button("🧘 ทำสมาธิ", key="continue_meditate"):
                    st.session_state.action_taken = "meditate"

    def _render_loop_reset_scene(self, state: GameState):
        """Render the time loop reset scene with detailed summary"""
        st.markdown(
            f"""
        ### 🔄 วัฏจักรกาลครั้งที่ {state.loop_count}
        
        เวลาเริ่มต้นใหม่อีกครั้ง... แต่คุณจำได้
        
        ผู้คนรอบตัวดำเนินชีวิตเหมือนเดิม แต่ในสายตาบางคน คุณเห็นประกายแห่งการจดจำ
        
        *การกระทำในอดีตเริ่มส่งผลต่อปัจจุบัน...*
        """
        )

        # Show detailed reset summary
        self._show_reset_summary(state)

        # Continue options
        st.subheader("🎯 เริ่มต้นใหม่:")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔍 สำรวจด้วยความระมัดระวัง", key="cautious_explore"):
                st.session_state.action_taken = "explore"

        with col2:
            if st.button("💭 ใช้ความทรงจำจากอดีต", key="memory_action"):
                st.session_state.action_taken = "use_memory"

        with col3:
            if st.button("🧘 ทำสมาธิเพื่อเตรียมพร้อม", key="prepare_meditate"):
                st.session_state.action_taken = "meditate"

    def _show_reset_summary(self, state: GameState):
        """Show comprehensive summary as flowing narrative"""
        st.subheader("📜 บทสรุปวัฏจักรที่ผ่านมา")

        # Create narrative summary instead of data tables
        karma = state.player.stats.karma
        decisions_count = len(state.decisions_made)
        days_used = state.current_day if state.current_day <= 7 else 7

        # Build narrative summary
        summary_parts = []

        # Opening
        summary_parts.append(
            f"ในวัฏจักรที่ผ่านไป คุณได้ใช้เวลา {days_used} วัน และตัดสินใจสำคัญไป {decisions_count} ครั้ง"
        )

        # Karma assessment with narrative
        if karma > 15:
            summary_parts.append(
                "การกระทำของคุณได้สร้างกรรมดีอย่างล้นเหลือ ดวงวิญญาณของคุณเปล่งประกายด้วยความบริสุทธิ์"
            )
        elif karma > 10:
            summary_parts.append("คุณได้สร้างกรรมดีไว้มากมาย ผู้คนจะจดจำความเมตตาของคุณ")
        elif karma > 0:
            summary_parts.append("คุณมีกรรมดีเล็กน้อย แต่ยังมีที่ให้ปรับปรุง")
        elif karma == 0:
            summary_parts.append("คุณรักษาสมดุลระหว่างดีและชั่วไว้ได้ ทางกลางคือภูมิปัญญา")
        elif karma > -10:
            summary_parts.append("คุณมีกรรมลบเล็กน้อย แต่ยังมีโอกาสแก้ไข")
        else:
            summary_parts.append("การกระทำของคุณได้สร้างกรรมลบไว้มาก เงาของความผิดติดตามคุณไป")

        # Time fragments and wisdom
        if state.time_fragments > 5:
            summary_parts.append(
                f"คุณรวบรวมเศษเวลาได้ {state.time_fragments} ชิ้น ซึ่งแสดงถึงความเข้าใจในธรรมชาติของเวลา"
            )

        if state.player.stats.wisdom > 20:
            summary_parts.append("ปัญญาของคุณได้เติบโตจนกลายเป็นปราชญ์ผู้ยิ่งใหญ่")
        elif state.player.stats.wisdom > 15:
            summary_parts.append("ปัญญาของคุณเติบโตขึ้นอย่างน่าประทับใจ")

        # Quests
        if state.active_quests:
            if len(state.active_quests) == 1:
                summary_parts.append(
                    f"คุณยังคงมีภารกิจ '{state.active_quests[0]}' ที่ต้องดำเนินการต่อ"
                )
            else:
                summary_parts.append(
                    f"คุณมีภารกิจ {len(state.active_quests)} อย่างที่รอการดำเนินการ"
                )

        # Future prediction
        if karma > 5:
            summary_parts.append(
                "\n\nในวัฏจักรหน้า ผู้คนจะต้อนรับคุณด้วยรอยยิ้ม และเปิดใจให้ความช่วยเหลือ กรรมดีที่คุณสั่งสมจะเป็นแสงนำทางในความมืด"
            )
        elif karma < -5:
            summary_parts.append(
                "\n\nในวัฏจักรหน้า ผู้คนจะหลีกเลี่ยงสายตาคุณ ความไม่ไว้วางใจจะเป็นเงาที่ตามติด แต่ยังมีโอกาสที่จะแก้ไขกรรมลบ"
            )
        else:
            summary_parts.append(
                "\n\nในวัฏจักรหน้า ทุกอย่างยังเป็นไปได้ ชะตากรรมยังไม่ถูกกำหนด และคุณยังมีอำนาจที่จะเปลี่ยนแปลงอนาคต"
            )

        # Display as flowing narrative
        complete_summary = " ".join(summary_parts)

        with st.container():
            st.markdown(f"*{complete_summary}*")

        # Simple stats for reference
        with st.expander("📊 ดูรายละเอียดเพิ่มเติม"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("การตัดสินใจ", decisions_count)
                st.metric("วันที่ใช้", days_used)
            with col2:
                st.metric("กรรม", karma)
                st.metric("ปัญญา", state.player.stats.wisdom)
            with col3:
                st.metric("เศษเวลา", state.time_fragments)
                st.metric("ภารกิจ", len(state.active_quests))

    def handle_user_input(self, game_engine: GameEngine):
        """Handle user input and actions - moved to main.py to avoid calling from render"""
        pass  # This method is now empty - logic moved to main.py
