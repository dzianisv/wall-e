import logging
from langchain_openai import ChatOpenAI
from langchain.agents import create_structured_chat_agent, AgentExecutor, load_tools
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.tools import YouTubeSearchTool
from youtube_captions_tool import YouTubeCaptionTool
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import MongoDBChatMessageHistory
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage

import threading


from config import Config

logger = logging.getLogger(__name__)

class LLM(object):
    def __init__(self, memory_window=8):
        self.llm = ChatOpenAI(
            openai_api_base=Config.openai_api_base, 
            openai_api_key=Config.openai_api_key,
            openai_proxy=Config.openai_proxy,
            temperature=0.7, 
            model=Config.openai_model,
        )
        self.chain = self._create_langchain()

    def _remember(self, session_id):
        # Create a MongoDB-backed chat message history for this user/session.
        mongodb_history = MongoDBChatMessageHistory(
            session_id=session_id,
            connection_string=Config.mongo_uri,
            database_name="walle",
            collection_name="chats",
        )
        # return mongodb_history
        # Wrap the message history in a conversation buffer memory.
        # return_messages=True ensures memory returns a list of Message objects instead of strings.
        return ConversationBufferMemory(
            memory_key="chat_history",
            chat_memory=mongodb_history,
            return_messages=True
        )
    
    def _create_langchain(self):
        # https://langchain-ai.github.io/langgraph/how-tos/create-react-agent/#usage
        tool_list = []

        # Attempt to load ddg-search tool
        try:
            tools = load_tools(["ddg-search"])
            tool_list.extend(tools)
        except Exception as e:
            logger.warning("DuckDuckGo search tool not available: %s", e)

        # Add YouTube search tool
        tool_list.append(YouTubeSearchTool())
        # Add YouTube captions tool
        tool_list.append(YouTubeCaptionTool())

        # Pull the structured chat agent prompt from hub
        system = (
            "You are a helpful assistant"
            "You may not need to use tools for every query - the user may just want to chat!"
        )

        memory = MemorySaver()
        return create_react_agent(self.llm, tools, state_modifier=system, checkpointer=memory)
        # agent_executor = AgentExecutor.from_agent_and_tools(
        #     agent=agent,
        #     tools=tools,
        #     verbose=False,
        #     handle_parsing_errors=True,
        #     max_iterations=4000,
        #     max_execution_time=60000
        # )
        # # https://github.com/langchain-ai/langchain/discussions/26337#discussioncomment-10618489
        # return RunnableWithMessageHistory(
        #     agent_executor,
        #     lambda session_id: self._remember(session_id),
        #     input_messages_key="input",
        #     history_messages_key="agent_scratchpad",
        # )

    def ask(self, prompt_str: str, session_id='test'):
        response = self.chain.invoke({"messages": [HumanMessage(content=prompt_str)]}, 
                                     {"session_id": session_id, "thread_id": threading.get_ident()}
                                     )

        logger.info("Got an answer for %s: %s", session_id, response)
        return response['messages'][-1].content