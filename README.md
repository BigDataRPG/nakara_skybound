# Nakara Skybound

**Nakara Skybound** (ตำนานนครากลับฟ้า) is an advanced interactive game simulation that combines LLM-powered NPCs, agent memory, strategic planning, and external knowledge integration via MCP (Model Context Protocol) and DeepWiki.

## Game Overview

**Nakara Skybound: วัฏจักรกาล** is a narrative-driven, time-loop adventure inspired by Thai mythology. Players explore the mystical city of Nakara, interact with AI-powered NPCs, and make decisions that influence the unfolding story across multiple eras. The game features:

- **Time Loops**: Experience repeating cycles where your choices and karma affect each new loop.
- **Dynamic World**: The city and its inhabitants evolve based on your actions, memories, and accumulated knowledge.
- **Strategic Choices**: Manage resources, relationships, and quests to uncover secrets and break the cycle.
- **AI NPCs**: Converse with intelligent NPCs who remember past interactions and adapt their behavior.
- **External Knowledge**: NPCs can access DeepWiki via MCP to provide lore, hints, or answer player questions.

Your goal is to unravel the mysteries of Nakara, restore balance, and ultimately escape the endless cycle.

## Features

- **LLM-Powered NPCs**: NPCs use large language models for dynamic, context-aware dialogue.
- **Agent Memory**: Both players and NPCs remember past actions, conversations, and world events.
- **Strategic Planning**: The game state and NPCs adapt strategies based on memory and context.
- **MCP/DeepWiki Integration**: NPCs can access external knowledge sources to answer player questions or enhance dialogue.
- **Emergent Narrative**: Player and NPC strategies combine for a rich, evolving story.

## Lessons & Structure

All interactive lessons and notebooks are in the `workshop/` folder:

- `workshop/lesson_01_intro_to_langgraph.ipynb`: Introduction to LangGraph and basic agent setup.
- `workshop/lesson_02_game_state_management.ipynb`: Advanced game state management, memory, and strategy.
- `workshop/lesson_03_ai_npcs_and_dialogue.ipynb`: AI-powered NPCs and intelligent dialogue systems.
- `workshop/lesson_04_ai_npc_memory_strategy.ipynb`: AI NPCs with memory, strategy, and LLM dialogue.
- `workshop/lesson_05_mcp_llm_game.ipynb`: Integrating MCP with LLMs for game NPCs.
- `workshop/lesson_06_mcp_ai_npc.ipynb`: Advanced game state, memory, strategy, and LLM-powered NPCs with MCP/DeepWiki.

## Streamlit Game Structure (`src/`)

The interactive game is implemented using [Streamlit](https://streamlit.io/) and organized as follows:

- **src/nakara_skybound/main.py**: Entry point for the Streamlit app. Handles UI rendering, user actions, and game loop.
- **src/nakara_skybound/game/game_engine.py**: Core game logic, state management, and decision processing.
- **src/nakara_skybound/game/save_system.py**: Save/load functionality for player progress.
- **src/nakara_skybound/game/time_system.py**: Time and era management, including time loops and era transitions.
- **src/nakara_skybound/game/ui_manager.py**: UI rendering logic for displaying game state, scenes, and options.
- **src/nakara_skybound/game/character.py**: Player and NPC character models, stats, inventory, and interactions.

**How it works:**

1. **Initialization**: When the app starts, it initializes the game engine, UI manager, and save system in the Streamlit session state.
2. **User Actions**: All user actions (moving, making decisions, time travel, etc.) are handled in a single function to ensure state consistency and avoid infinite loops.
3. **Game State Rendering**: The UI manager displays the current game state, available actions, and narrative updates.
4. **State Updates**: After each action, the game state is updated and the UI is refreshed to reflect changes.
5. **Persistence**: The save system allows players to save and load their progress.

This modular structure makes it easy to extend the game with new features, scenes, or mechanics.

## Requirements

- Python 3.12+
- [Poetry](https://python-poetry.org/) for dependency management
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [LangChain](https://github.com/langchain-ai/langchain)
- [langgraph](https://github.com/langchain-ai/langgraph)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- Access to OpenAI API and MCP-compatible endpoints (e.g., DeepWiki)

## Quick Start

1. Clone the repository.
2. Install dependencies using Poetry:
    ```bash
    poetry install
    ```
3. Set your OpenAI API key and any required environment variables in a `.env` file.
4. Open and run the Jupyter notebooks in order, starting from the introduction:
    - `workshop/lesson_01_intro_to_langgraph.ipynb`
    - `workshop/lesson_02_game_state_management.ipynb`
    - `workshop/lesson_03_ai_npcs_and_dialogue.ipynb`
    - `workshop/lesson_04_ai_npc_memory_strategy.ipynb`
    - `workshop/lesson_05_mcp_llm_game.ipynb`
    - `workshop/lesson_06_mcp_ai_npc.ipynb`
    - You can launch Jupyter via Poetry:
      ```bash
      poetry run jupyter notebook
      ```

## Example: Ask an NPC with DeepWiki

```python
from openai import OpenAI

client = OpenAI()
resp = client.responses.create(
    model="gpt-4o-mini",
    tools=[{
        "type": "mcp",
        "server_label": "deepwiki",
        "server_url": "https://mcp.deepwiki.com/mcp",
        "require_approval": {
            "never": {"tool_names": ["ask_question", "read_wiki_structure"]}
        }
    }],
    input="What is the legend of Nakara Skybound?",
)
print(resp.output_text)
```

## Credits

- Inspired by Thai mythology and modern AI research.
- Uses [DeepWiki](https://deepwiki.com/) and [MCP](https://mcpmarket.com/) for external knowledge.

## License

MIT License

