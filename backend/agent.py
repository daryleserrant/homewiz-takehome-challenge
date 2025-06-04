from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, Tool
from langchain.tools import StructuredTool
from langchain.tools.render import format_tool_to_openai_tool
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from tools import validate_email, validate_phone, validate_move_in_date, validate_beds, store_prospect_info, check_availability, book_tour
from langchain.memory import ConversationBufferMemory
from utils import config
from schema import BookTourInput, ProspectInfo

import os

# Set up configuration from environment variables for deployment in Render or similar platforms.
# You can set these environment variables in your deployment platform.
# If you have a config.ini file, you can read it instead.
#os.environ["OPENAI_API_KEY"] = config["SETTINGS"]["OPENAI_API_KEY"]

# memory_store and agent_store hold per-session objects.
# In production, you'd want to periodically clean these up based on TTL or usage limits.
memory_store = {}
agent_store = {}

def get_or_create_agent_executor(session_id: str) -> AgentExecutor:
    """
    Get or create an agent executor for the given session ID.
    If it doesn't exist, initialize a new one.
    """
    if session_id not in agent_store:
        agent_store[session_id] = create_agent_executor(session_id)
    
    return agent_store[session_id]


def create_agent_executor(session_id: str) -> AgentExecutor:
    """
    Initialize the agent executor with the user-specific tools and prompt.
    """
    tools = [
        Tool(
            name="validate_email",
            func= validate_email,
            description="Validate email address. Returns True if the email address is valid, false otherwise.",
        ),
        Tool(
            name="validate_phone",
            func=validate_phone,
            description="Validate phone number. Returns True if the phone number is valid, false otherwise.",
        ),
        Tool(
            name="validate_move_in_date",
            func=validate_move_in_date,
            description="Validate a move-in date.",
        ),
        Tool(
            name="validate_beds",
            func=validate_beds,
            description="Validate the number of bedrooms requested.",
        ),
        StructuredTool.from_function(
            name="store_prospect_info",
            func=store_prospect_info,
            description="Store prospect information in the database. Returns the ID of the stored information.",
            args_schema=ProspectInfo
        ),
        Tool(
            name="check_availability",
            func=check_availability,
            description="Check inventory for available properties with the specified number of beds. Returns the unit ID if available. Otherwise returns None.",
        ),
        StructuredTool.from_function(
            name="book_tour",
            func=book_tour,
            description="Book a tour for the prospect and send a confirmation email. Returns a confirmation message.",
            args_schema= BookTourInput
        )
    ]
    oai_tools = [format_tool_to_openai_tool(tool) for tool in tools]

    model = ChatOpenAI(model_name=config["SETTINGS"]["MODEL"], temperature=0.0)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful leasing assistant. Ask the user for their name, email, phone number, desired move-in date, and number of bedrooms.
         Do not search availability or confirm a tour until all details are collected and validated for correctness. If no available properties are found, inform the user and suggest they check back later.
         If there are no available time slots for a tour, inform the user and suggest they check back later."""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
    )
    memory_store[session_id] = memory

    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_tool_messages(x["intermediate_steps"]),
            "chat_history": lambda x: memory.load_memory_variables({})["chat_history"]
        }
        | prompt
        | model.bind(tools=oai_tools)
        | OpenAIToolsAgentOutputParser()
    )

    agent_executor = AgentExecutor(agent=agent, tools=tools, memory = memory, verbose=True, return_intermediate_steps=False)

    agent_store[session_id] = agent_executor

    return agent_executor

