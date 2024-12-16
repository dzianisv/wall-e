from langchain.memory import Memory
from langchain.schema import BaseMessage

class MongoConversationMemory(Memory):
    def __init__(self, user_id: str, store: MongoMemoryStore):
        self.user_id = user_id
        self.store = store

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        messages = self.store.get_conversation(self.user_id)
        return {"chat_history": messages}

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        # Append the new human and AI messages to the conversation
        messages = self.store.get_conversation(self.user_id)
        if "input" in inputs:
            messages.append(HumanMessage(content=inputs["input"]))
        if "output" in outputs:
            messages.append(AIMessage(content=outputs["output"]))
        self.store.save_conversation(self.user_id, messages)

    def clear(self):
        self.store.save_conversation(self.user_id, [])
