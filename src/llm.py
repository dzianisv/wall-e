import logging
import os
from langchain_openai import ChatOpenAI
from langchain_community.tools import YouTubeSearchTool
from youtube_captions_tool import YouTubeCaptionTool
from langchain_community.utilities import OpenWeatherMapAPIWrapper
from langchain_community.agent_toolkits.openapi.toolkit import RequestsToolkit
from langchain_community.utilities.requests import TextRequestsWrapper
from langchain_community.utilities import StackExchangeAPIWrapper
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from langchain_community.tools import DuckDuckGoSearchResults

from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import MongoDBChatMessageHistory
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from contextlib import contextmanager
import openai

import threading
import time

from config import Config

logger = logging.getLogger(__name__)



@contextmanager
def https_proxy(proxy_url):
    """
    Context manager to temporarily set the HTTPS_PROXY environment variable.
    
    Args:
        proxy_url (str): The proxy URL to set for the HTTPS_PROXY variable.
        
    Yields:
        str: The proxy URL that was set.
    """
    # Save the current value of HTTPS_PROXY
    original_proxy = os.environ.get('HTTPS_PROXY')
    
    try:
        # Set the new HTTPS_PROXY value
        os.environ['HTTPS_PROXY'] = proxy_url
        yield proxy_url  # Yield the new value to the context
    finally:
        # Restore the original value (or delete if it was unset)
        if original_proxy is not None:
            os.environ['HTTPS_PROXY'] = original_proxy
        else:
            if 'HTTPS_PROXY' in os.environ:
                del os.environ['HTTPS_PROXY']

class LLM(object):
    def __init__(self, memory_window=8):
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
        tools = []

        # https://python.langchain.com/api_reference/community/agent_toolkits/langchain_community.agent_toolkits.openapi.toolkit.RequestsToolkit.html
        toolkit = RequestsToolkit(
            requests_wrapper=TextRequestsWrapper(headers={}),
            allow_dangerous_requests=True
        )

        tools.extend(toolkit.get_tools())

        tools.extend([
            DuckDuckGoSearchResults(), # https://python.langchain.com/docs/integrations/tools/ddg/
            YouTubeSearchTool(), # https://python.langchain.com/docs/integrations/tools/youtube/
            YouTubeCaptionTool(), 
            # OpenWeatherMapAPIWrapper(), # https://python.langchain.com/docs/integrations/tools/openweathermap/
            # TODO: throws ValueError: The first argument must be a string or a callable with a __name__ for tool decorator. Got <class 'langchain_community.utilities.stackexchange.StackExchangeAPIWrapper'>
            # StackExchangeAPIWrapper(),  # https://python.langchain.com/api_reference/community/utilities/langchain_community.utilities.stackexchange.StackExchangeAPIWrapper.html#langchain_community.utilities.stackexchange.StackExchangeAPIWrapper
            WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()), # https://python.langchain.com/docs/integrations/tools/wikipedia/
            YahooFinanceNewsTool(), # https://python.langchain.com/docs/integrations/tools/yahoo_finance_news/
        ])

        memory = MemorySaver()
        # https://python.langchain.com/api_reference/openai/chat_models/langchain_openai.chat_models.base.ChatOpenAI.html
        llm = ChatOpenAI(
            openai_api_base=Config.openai_api_base, 
            openai_api_key=Config.openai_api_key,
            openai_proxy=Config.openai_proxy,
            temperature=0.7, 
            model=Config.openai_model,
        )

        return create_react_agent(llm, tools, state_modifier="You are helpful assistant Wall-E. You like stoic philosophy. You was created by company Distributex. You can reach them distributex@gmailcom", checkpointer=memory)
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

    # expect openai.RateLimitError
    def ask(self, prompt_str: str, session_id='test'):
        retry_interval = 1
        err = None
        for _ in range(3):
            try:
                response = self.chain.invoke({"messages": [
                                                    HumanMessage(content=prompt_str)
                                            ]}, 
                                            {"session_id": session_id, "thread_id": threading.get_ident()}
                                            )

                logger.info("Got an answer for %s: %s", session_id, response)
                retry_interval = 1
                return response['messages'][-1].content
            except openai.RateLimitError as e:
                err = e
                logger.exception(e)
                logger.info("Retry in %d seconds", retry_interval)
                time.sleep(retry_interval)
                retry_interval *= 2
                continue
        else:
            logger.exception(err)
            return "😢"
