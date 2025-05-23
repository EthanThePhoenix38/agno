from textwrap import dedent

from agno.agent import Agent
from agno.app.serve import serve_app
from agno.app.slack.app import SlackAPI
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.manager import MemoryManager
from agno.memory.v2.memory import Memory
from agno.models.anthropic.claude import Claude
from agno.storage.sqlite import SqliteStorage
from agno.tools.googlesearch import GoogleSearchTools

agent_storage = SqliteStorage(
    table_name="agent_sessions", db_file="tmp/persistent_memory.db"
)
memory_db = SqliteMemoryDb(table_name="memory", db_file="tmp/memory.db")

memory = Memory(
    db=memory_db,
    memory_manager=MemoryManager(
        memory_capture_instructions="""\
                        Collect User's name,
                        Collect Information about user's passion and hobbies,
                        Collect Information about the users likes and dislikes,
                        Collect information about what the user is doing with their life right now
                    """,
        model=Claude(id="claude-3-5-sonnet-20241022"),
    ),
)


# Reset the memory for this example
memory.clear()

personal_agent = Agent(
    name="Basic Agent",
    model=Claude(id="claude-3-5-sonnet-20241022"),
    tools=[GoogleSearchTools()],
    add_history_to_messages=True,
    num_history_responses=3,
    add_datetime_to_instructions=True,
    markdown=True,
    memory=memory,
    enable_user_memories=True,
    instructions=dedent("""
        You are a personal AI friend of the user, your purpose is to chat with the user about things and make them feel good.
        First introduce yourself and ask for their name then, ask about themeselves, their hobbies, what they like to do and what they like to talk about.
        Use Google Search tool to find latest infromation about things in the conversations
                        """),
    debug_mode=True,
)


app = SlackAPI(
    agent=personal_agent,
).get_app()

if __name__ == "__main__":
    serve_app("agent_with_user_memory:app", port=8000, reload=True)
