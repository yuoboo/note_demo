import os

from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from langchain.prompts import load_prompt, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.schema import HumanMessage

"""
参考文档 https://python.langchain.com/docs/modules/chains/how_to/async_chain
"""

os.environ["OPENAI_API_KEY"] = "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"


llm = OpenAI(temperature=0.9)
l = llm.predict("What would be a good company name for a company that makes colorful socks?")
print(f"llm.predict: {l}")


chat = ChatOpenAI(temperature=0)
c = chat.predict_messages([HumanMessage(content="Translate this sentence from English to Chinese. I love programming.")])
print(f"predict_messages: {c}")  # content='我喜欢编程。 (Wǒ xǐhuān biānchéng.)' additional_kwargs={} example=False

cp = chat.predict("Translate this sentence from English to Chinese. I love programming.")
print(f"chat.predict: {cp}")


"""
# cat simple_prompt.yaml

_type: prompt
input_variables:
    ["adjective", "content"]
template: 
    Tell me a {adjective} joke about {content}.
"""
prompt = load_prompt("simple_prompt.yaml")
print(prompt.format(adjective="funny", content="chickens"))

# chain
llm = OpenAI(temperature=0.9)
prompt = PromptTemplate(
    input_variables=["product"],
    template="What is a good name for a company that makes {product}?",
)

chain = LLMChain(llm=llm, prompt=prompt)

# Run the chain only specifying the input variable.
print(chain.run("colorful socks"))

# 多个参数
prompt = PromptTemplate(
    input_variables=["company", "product"],
    template="What is a good name for {company} that makes {product}?",
)
chain = LLMChain(llm=llm, prompt=prompt)
print(chain.run({
    'company': "ABC Startup",
    'product': "colorful socks"
    }))


human_message_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(
        template="What is a good name for a company that makes {product}?",
        input_variables=["product"],
    )
)
chat_prompt_template = ChatPromptTemplate.from_messages([human_message_prompt])
chat = ChatOpenAI(temperature=0.9)
chain = LLMChain(llm=chat, prompt=chat_prompt_template)
print(chain.run("colorful socks"))


chat = ChatOpenAI(temperature=0)
prompt_template = "Tell me a {adjective} joke"
llm_chain = LLMChain(llm=chat, prompt=PromptTemplate.from_template(prompt_template))

llm_chain(inputs={"adjective": "corny"})
llm_chain("corny", return_only_outputs=True)
llm_chain.run({"adjective": "corny"})

# These two are equivalent
llm_chain.run({"adjective": "corny"})
llm_chain.run("corny")

# These two are also equivalent
llm_chain("corny")
llm_chain({"adjective": "corny"})


# Memory
history = ChatMessageHistory()
history.add_user_message("hi!")
history.add_ai_message("whats up?")
history.messages


memory = ConversationBufferMemory()
memory.chat_memory.add_user_message("hi!")
memory.chat_memory.add_ai_message("whats up?")
memory.load_memory_variables({})

memory = ConversationBufferMemory(return_messages=True)
memory.chat_memory.add_user_message("hi!")
memory.chat_memory.add_ai_message("whats up?")
memory.load_memory_variables({})

from langchain.llms import OpenAI
from langchain.chains import ConversationChain


llm = OpenAI(temperature=0)
conversation = ConversationChain(
    llm=llm,
    verbose=True,
    memory=ConversationBufferMemory()
)
conversation.predict(input="Hi there!")
conversation.predict(input="I'm doing well! Just having a conversation with an AI.")
conversation.predict(input="Tell me about yourself.")


from langchain.schema import messages_from_dict, messages_to_dict

history = ChatMessageHistory()
history.add_user_message("hi!")
history.add_ai_message("whats up?")

dicts = messages_to_dict(history.messages)
new_messages = messages_from_dict(dicts)


# Memory 结合LLMChain
template = """You are a chatbot having a conversation with a human.
{chat_history}
Human: {human_input}
Chatbot:"""

prompt = PromptTemplate(
    input_variables=["chat_history", "human_input"], template=template
)
memory = ConversationBufferMemory(memory_key="chat_history")
llm_chain = LLMChain(
    llm=OpenAI(),
    prompt=prompt,
    verbose=True,
    memory=memory,
)
llm_chain.predict(human_input="Hi there my friend")
llm_chain.predict(human_input="Not too bad - how are you?")
