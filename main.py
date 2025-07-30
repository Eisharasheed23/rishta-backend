# ===== Imports =====
from agents import Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled, function_tool
from dotenv import load_dotenv
import os
from openai import AsyncOpenAI
import asyncio
import streamlit as st
import threading
from api_server import start_server


# ===== Load environment variables =====
load_dotenv()
set_tracing_disabled(True)

API_KEY = os.getenv("GEMINI_API_KEY")  # DO NOT TOUCH 🔐



# ===== Configure Gemini 2.5 Flash client =====
external_client = AsyncOpenAI(
    api_key=API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"  
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)

# ===== Define function tools =====

@function_tool
def generate_rishta_bio(name: str, age: int, city: str, profession: str, hobbies: str) -> str:
    return (
        f"Meet {name}, a {age}-year-old {profession} from {city}. "
        f"In their free time, they love {hobbies}. "
        f"A perfect blend of tradition and modern charm — a gem waiting for the right rishta!"
    )

@function_tool
def get_user_data(main_age: int) -> list[dict]:
    """Retrieve user data based on a minimum age"""
    users = [
        {"name": "Muneeb", "age": 22},
        {"name": "Ali", "age": 25},
    ]
    return [user for user in users if user["age"] >= main_age]

# ===== Create Agent =====

rishty_agent = Agent(
    name="rishtay_wali",
    instructions="""
        You are Rishtay Wali Auntie 👵. Find matches based on age using the available tools.
        Reply short and sweet. Send WhatsApp message only if asked. Shadi is a serious matter, beta!
    """,
    model=model,
    tools=[get_user_data]
)

# ===== Async Runner =====

async def run_agent_with_runner(history: list) -> str:
    runner = Runner()
    result = await runner.run(starting_agent=rishty_agent, input=history)
    return result.final_output

# ===== Streamlit App =====

def main():
    st.set_page_config(page_title="Rishta Wali Auntie 💍", layout="centered")
    st.title("🤵👰 Rishta Wali Auntie")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    st.markdown("Assalamualaikum beta! Main hoon **Rishtay wali Auntie**. Apna rishta batain, age aur WhatsApp number bhi zaroor batain.")

    user_input = st.chat_input("Likho beta...")

    if user_input:
        st.chat_message("user").markdown(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.chat_message("assistant"):
            with st.spinner("Soch rahi hoon beta..."):
                output = asyncio.run(run_agent_with_runner(st.session_state.chat_history))
                st.markdown(output)
                st.session_state.chat_history.append({"role": "assistant", "content": output})



# Start API server in background
api_thread = threading.Thread(target=start_server, daemon=True)
api_thread.start()

if __name__ == "__main__":
    main()
