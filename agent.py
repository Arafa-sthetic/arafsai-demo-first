from dotenv import load_dotenv
import os
import asyncio
import logging
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import google, noise_cancellation

# আপনার প্রয়োজনীয় মডিউলগুলো এখানে ইমপোর্ট করুন
from auto_thinking import arafsaiAutoThinking
from arafsai_prompt import behavior_prompts, Reply_prompts
from arafsai_screenshot import screenshot_tool
from arafsai_google_search import google_search, get_current_datetime
from memory_store import ConversationMemory
from memory_interceptor import MEMORY_KEYWORDS
from arafsai_get_whether import get_weather
from arafsai_window_CTRL import open, close, folder_file
from arafsai_file_open import Play_file
from keyboard_mouse_CTRL import move_cursor_tool, mouse_click_tool, scroll_cursor_tool, type_text_tool, press_key_tool, swipe_gesture_tool, press_hotkey_tool, control_volume_tool

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ENABLE_MEMORY_INTERCEPTOR = False
memory = ConversationMemory(user_id="Arafsai_User")

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=behavior_prompts,
                         tools=[
                             google_search, get_current_datetime, get_weather, open, close,
                             folder_file, Play_file, screenshot_tool, move_cursor_tool,
                             mouse_click_tool, scroll_cursor_tool, type_text_tool,
                             press_key_tool, press_hotkey_tool, control_volume_tool,
                             swipe_gesture_tool
                         ])

async def entrypoint(ctx: agents.JobContext):
    auto_thinker = arafsaiAutoThinking()
    print("🧠 arafsaiAutoThinking background assistant started")
    
    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(voice="Leda")
    )
    
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
            video_enabled=False 
        ),
    )
    await ctx.connect()
    print("✅ Connected to room, waiting for audio input...")
    
    await session.generate_reply(instructions=Reply_prompts)

if __name__ == "__main__":
    # সার্ভারে চালানোর জন্য GUI অংশটি পুরোপুরি মুছে ফেলা হয়েছে
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))