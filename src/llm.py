import os
import logging
from langchain_openai import ChatOpenAI
from langchain.agents import create_structured_chat_agent, AgentExecutor, load_tools
from langchain_community.tools import YouTubeSearchTool
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder, ChatPromptTemplate
from langchain import hub
from youtube_captions_tool import YouTubeCaptionTool
from config import Config
from bson.objectid import ObjectId
from langchain.mongodb import MongoDBChatMessageHistory

logger = logging.getLogger(__name__)



class LLM(object):
    def __init__(self, user_id: str, memory_window=8):
        self.user_id = user_id
        
        chat_message_history = MongoDBChatMessageHistory(
            session_id=ObjectId(),
            connection_string=Config.mongo_uri
            database_name="walle",
            collection_name="chats",
        )

        self.llm = ChatOpenAI(
            openai_api_base=Config.openai_api_base, 
            openai_api_key=Config.openai_api_key,
            openai_proxy=Config.openai_proxy,
            temperature=0.7, 
            model=Config.openai_model,
        )

        self.chain = self._init_agent()

    def _init_agent(self):
        # Load various search tools - ensure they are installed and configured
        # For demonstration, we load ddg-search, and others if available.
        tool_list = []
        # Add DuckDuckGo search if available
        try:
            tools = load_tools(["ddg-search"])
            tool_list.extend(tools)
        except Exception as e:
            logger.warning("DuckDuckGo search tool not available: %s", e)

        # Add YouTube search tool
        tool_list.append(YouTubeSearchTool())
        # Add YouTube captions tool
        tool_list.append(YouTubeCaptionTool())

        # You can similarly add Bing, Google, etc. if you've set them up.
        # For Bing or Google, you'd need API keys and possibly different load_tools calls.

        # Structured Chat Agent prompt
        prompt = hub.pull("hwchase17/structured-chat-agent")    

        agent = create_structured_chat_agent(
            tools=tool_list,
            llm=self.llm,
            prompt=prompt
        )

        agent_executor = AgentExecutor(
            agent=agent, 
            tools=tool_list, 
            verbose=True, 
            memory=self.memory,
            return_intermediate_steps=True, 
            handle_parsing_errors=True
        )

        return agent_executor

    def ask(self, prompt):      
        response = self.chain.invoke({"input": prompt})
        return response['output'] if 'output' in response else response.get('text', '')

