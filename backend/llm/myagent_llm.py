from langchain_ollama import ChatOllama
from langchain.callbacks.base import BaseCallbackHandler

def get_myagent_llm(streaming: bool = False):
	llm = ChatOllama(
		model = "hermes3:8b",
		base_url = "http://127.0.0.1:11434",
		temperature = 0.7,
		num_ctx = 4096,
		streaming = streaming
	)
	return llm

