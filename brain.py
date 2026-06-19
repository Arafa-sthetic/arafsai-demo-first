from dotenv import load_dotenv
import os
import asyncio
import logging
import subprocess
import sys
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import google, noise_cancellation

# আপনার লোকাল মডিউলগুলো ইমপোর্ট করুন
from arafsai_prompt import behavior_prompts, Reply_prompts
from arafsai_google_search import google_search, get_current_datetime
from arafsai_get_whether import get_weather
# হার্ডওয়্যার কন্ট্রোল টুলস সার্ভারে রান করলে এরর দিতে পারে, 
# তাই প্রয়োজনবোধে সার্ভারে এগুলোর বদলে ডামি টুলস ব্যবহার করবেন।
from arafsai_window_CTRL import open, close, folder_file
from arafsai_file_open import Play_file
from keyboard_mouse_CTRL import (move_cursor_tool, mouse_click_tool, scroll_cursor_tool, 
                                 type_text_tool, press_key_tool, swipe_gesture_tool, 
                                 press_hotkey_tool, control_volume_tool)

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# সার্ভারে GUI বন্ধ রাখার ফ্ল্যাগ
# Render-এর Environment Variables এ ENVIRONMENT = production সেট করুন
IS_SERVER = os.getenv("ENVIRONMENT") == "production"

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=behavior_prompts,
                         tools=[
                             google_search, get_current_datetime, get_weather, open, close,
                             folder_file, Play_file, move_cursor_tool, mouse_click_tool,
                             scroll_cursor_tool, type_text_tool, press_key_tool, 
                             press_hotkey_tool, control_volume_tool, swipe_gesture_tool
                         ])

async def entrypoint(ctx: agents.JobContext):
    print("🚀 Starting agent session...")
    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(voice="Charon")
    )
    
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
            video_enabled=True 
        ),
    )
    await ctx.connect()
    print("✅ Connected to room!")
    await session.generate_reply(instructions=Reply_prompts)

if __name__ == "__main__":
    # যদি সার্ভার হয়, তবে GUI রান করার চেষ্টা করবে না
    if not IS_SERVER:
        try:
            gui_path = os.path.join(os.path.dirname(__file__), "arafsai_gui.py")
            if os.path.exists(gui_path):
                subprocess.Popen([sys.executable, gui_path])
        except Exception as e:
            print(f"GUI start failed: {e}")

    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))