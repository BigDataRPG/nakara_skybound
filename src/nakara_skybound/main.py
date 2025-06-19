import streamlit as st
from game.game_engine import GameEngine
from game.save_system import SaveSystem
from game.time_system import TimeEra
from game.ui_manager import UIManager


def handle_user_actions(game_engine: GameEngine):
    """Handle all user actions in one place to avoid infinite loops"""

    # Handle location change with optional day advancement
    if hasattr(st.session_state, "new_location"):
        state = game_engine.get_current_state()
        old_location = state.current_location
        state.current_location = st.session_state.new_location

        # Check if fast travel was used (advances day)
        if hasattr(st.session_state, "advance_day") and st.session_state.advance_day:
            state.current_day += 1
            st.success(
                f"คุณได้เดินทางอย่างรวดเร็วจาก {old_location} ไปยัง {state.current_location} (ใช้เวลา 1 วัน)"
            )
            del st.session_state.advance_day
        else:
            st.success(f"คุณได้เดินทางจาก {old_location} ไปยัง {state.current_location}")

        # Reset scene to standard
        state.current_scene = "standard"

        # Clear action result
        if hasattr(st.session_state, "last_action_result"):
            del st.session_state.last_action_result

        del st.session_state.new_location
        st.rerun()

    # Handle loop trigger with story summary
    if hasattr(st.session_state, "trigger_loop"):
        result = game_engine.trigger_time_loop()
        if result["success"]:
            st.success(f"วัฏจักรเวลารีเซ็ตแล้ว! รอบที่ {result['loop_count']}")
            st.info(result["narrative"])

            # Store loop result with cycle summary
            cycle_summary = f"รอบที่ {result['loop_count'] - 1} สิ้นสุดแล้ว - กรรมสุดท้าย: {game_engine.get_current_state().player.stats.karma}, การตัดสินใจ: {len(game_engine.get_current_state().decisions_made)} ครั้ง"

            st.session_state.last_action_result = {
                "narrative": result["narrative"] + f"\n\n📊 {cycle_summary}",
                "consequences": [],
                "next_options": [
                    {"id": "explore", "text": "เริ่มต้นใหม่"},
                    {"id": "meditate", "text": "ทำความเข้าใจกับการรีเซ็ต"},
                ],
            }

            # Change scene
            state = game_engine.get_current_state()
            state.current_scene = "action_result"

        del st.session_state.trigger_loop

    # Handle action taken with enhanced consequence processing
    if hasattr(st.session_state, "action_taken"):
        action = st.session_state.action_taken

        # Process the action
        result = game_engine.make_decision("general_action", action)

        # Store the result for display
        st.session_state.last_action_result = result

        # Change scene to show action result
        state = game_engine.get_current_state()
        state.current_scene = "action_result"

        # Apply all consequences including day advancement
        if "consequences" in result:
            for consequence in result["consequences"]:
                if consequence["type"] == "stat_change":
                    state.player.modify_stat(consequence["stat"], consequence["value"])
                elif consequence["type"] == "time_fragment":
                    state.time_fragments += consequence["amount"]
                elif consequence["type"] == "day_advance":
                    state.current_day += consequence["amount"]
                    # Check if 7 days completed
                    if state.current_day >= 7:
                        st.warning("⚠️ วัฏจักรเวลาครบ 7 วัน! เตรียมพร้อมสำหรับการสรุป...")
                elif consequence["type"] == "item_gain":
                    from game.character import Item

                    item_data = consequence["item"]
                    # Create proper Item object
                    item = Item(
                        id=item_data["id"],
                        name=item_data["name"],
                        description=item_data["description"],
                        type=item_data["type"],
                        power=item_data.get("power", 0),
                        magical_properties=item_data.get("magical_properties", {}),
                    )
                    state.player.add_item(item)
                elif consequence["type"] == "quest_start":
                    quest_name = consequence.get("quest_name", "ภารกิจใหม่")
                    if quest_name not in state.active_quests:
                        state.active_quests.append(quest_name)

        # Clear the action
        del st.session_state.action_taken
        st.rerun()  # Force immediate update

    # Handle pending time travel
    if hasattr(st.session_state, "pending_time_travel"):
        target_era = st.session_state.pending_time_travel
        result = game_engine.travel_through_time(target_era)

        if result["success"]:
            st.success(f"เดินทางสู่{target_era.value}สำเร็จ!")
            if "narrative" in result:
                st.info(result["narrative"])

            # Store travel result
            st.session_state.last_action_result = {
                "narrative": result.get("narrative", ""),
                "consequences": [{"type": "era_change", "new_era": target_era.value}],
                "next_options": [
                    {"id": "explore", "text": "สำรวจยุคใหม่"},
                    {"id": "meditate", "text": "ทำความเข้าใจกับสิ่งรอบตัว"},
                    {"id": "talk", "text": "คุยกับผู้คนในยุคนี้"},
                ],
            }

            # Change scene
            state = game_engine.get_current_state()
            state.current_scene = "action_result"
        else:
            st.error(result["message"])

        del st.session_state.pending_time_travel


def main():
    st.set_page_config(
        page_title="ตำนานนครากลับฟ้า: วัฏจักรกาล",
        page_icon="🌀",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize game systems
    if "game_engine" not in st.session_state:
        st.session_state.game_engine = GameEngine()
        st.session_state.ui_manager = UIManager()
        st.session_state.save_system = SaveSystem()

    # Game header with clean description
    st.markdown(
        """
    # 🌀 ตำนานนครางกลับฟ้า: วัฏจักรกาล
    ## *Nakara Skybound: Time Cycle*
    
    **"เวลา...ไม่ใช่แค่สิ่งที่ผ่านไป แต่มันย้อนกลับมา…ทวงสิ่งที่เราทำไว้"**
    """
    )

    # Main game loop
    game_engine = st.session_state.game_engine
    ui_manager = st.session_state.ui_manager

    # Handle user actions first
    handle_user_actions(game_engine)

    # Render current game state
    ui_manager.render_game_state(game_engine.get_current_state())


if __name__ == "__main__":
    main()
