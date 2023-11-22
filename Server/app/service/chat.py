from pydantic import BaseModel, Field
import json
from langchain.schema.agent import AgentActionMessageLog, AgentFinish
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.chat_models import ChatOpenAI, AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain import hub
from langchain.memory import ConversationBufferMemory
from langchain.tools.render import render_text_description
from typing import Optional
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools import BaseTool
from supabase import create_client, Client
from supabase.client import ClientOptions
from langchain.embeddings import OpenAIEmbeddings, AzureOpenAIEmbeddings
from langchain.agents.format_scratchpad import format_log_to_messages
from langchain.agents.output_parsers import JSONAgentOutputParser
from dotenv import load_dotenv
from app.service.supabase_client import SupabaseClient

load_dotenv()


class Response(BaseModel):
    """Final response to the question being asked"""

    intent: str = Field(description="The intent you judged")


def parse(output):
    # If no function was invoked, return to user
    if "function_call" not in output.additional_kwargs:
        return AgentFinish(return_values={"output": output.content}, log=output.content)

    # Parse out the function call
    function_call = output.additional_kwargs["function_call"]
    name = function_call["name"]
    inputs = json.loads(function_call["arguments"])

    # If the Response function was invoked, return to the user with the function inputs
    if name == "Response":
        return AgentFinish(return_values=inputs, log=str(function_call))
    # Otherwise, return an agent action
    else:
        return AgentActionMessageLog(
            tool=name, tool_input=inputs, log="", message_log=[output]
        )


def predict_intent(input, messages=[]):
    history = ""
    for message in messages:
        if message.role == "user":
            history += "USER:" + message.content + "\n"
        else:
            history += "AI:" + message.content + "\n"

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a rigorous and serious customer service expert.Please identify the customer's latest intentions based on the conversation records and the customer's latest news provided below. Please follow these steps:
                1. Determine the customer's intention and select the most suitable option from the following options:
                    S: Indicates that the customer starts a conversation (saying hello, greetings, etc.);
                    W: Indicates that the customer has not described the problem clearly and is providing information or explaining the situation and needs to wait for the user to send more descriptions;
                    Q: Indicates that the customer has raised a complete question and needs customer service to answer it;
                    E: Indicates completion of dialogue, end of dialogue, thanks, etc.;
                Only answer one intent.
                """,
            ),
            (
                "user",
                """
                conversation records is（use\`\`\`split）：
                \`\`\`"""
                + history
                + """
                \`\`\`
                latest messgae is：{input}
             """,
            ),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    llm = AzureChatOpenAI(
        azure_deployment="gpt-4",
        openai_api_version="2023-05-15",
        azure_endpoint="https://seedlings-ejp.openai.azure.com/",
        api_key="2cb70053536b4e1b8d76dfdb09ad2459",
        base_url=""
    )

    agent = (
        {
            "input": lambda x: x["input"],
            # Format agent scratchpad from intermediate steps
            "agent_scratchpad": lambda x: format_to_openai_function_messages(
                x["intermediate_steps"]
            ),
        }
        | prompt
        | llm
        | parse
    )

    agent_executor = AgentExecutor(tools=[], agent=agent, verbose=True)

    return agent_executor.invoke(
        {"input": input},
        return_only_outputs=True,
    )


def query_similar_by_supabase(query: str, knowledge_base_id: int):
    embeddings_model = AzureOpenAIEmbeddings(
        azure_endpoint="https://seedlings.openai.azure.com/",
        openai_api_key="49c6eee59eb642f29857eb571b0fb729",
        azure_deployment="text-embedding-ada-002",
        openai_api_version="2023-05-15",
    )

    embedding = embeddings_model.embed_query(query)

    supabase = SupabaseClient()

    res = supabase.rpc(
        "match_knowledge_with_meta",
        {
            "query_embedding": embedding,
            "match_count": 10,
            "knowledge_base_id": knowledge_base_id,
        },
    ).execute()

    datas = [data for data in res.data if data["similarity"] > 0.85]

    context = ""
    for data in datas:
        struct_data = json.loads(data["content"])
        context += (
            "question:"
            + struct_data["question"]
            + "\n"
            + "answer:"
            + struct_data["answer"]
            + "\n"
        )

    return context


def chat(
    input: str,
    memory: ConversationBufferMemory,
    role_prompt: str,
    knowledge_base_id: int,
):
    class CustomSearchTool(BaseTool):
        name = "custom_search"
        description = (
            "useful for when you need to answer questions about medical beauty"
        )
        # description = "useful for when you need to answer questions about tax"

        def _run(
            self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
        ) -> str:
            """Use the tool."""
            return query_similar_by_supabase(query, knowledge_base_id)

        async def _arun(
            self,
            query: str,
            run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
        ) -> str:
            """Use the tool asynchronously."""
            raise NotImplementedError("custom_search does not support async")

    tools = [CustomSearchTool()]

    prompt = hub.pull("hwchase17/react-chat-json")

    chat_model = AzureChatOpenAI(
        azure_deployment="gpt-4",
        openai_api_version="2023-05-15",
        azure_endpoint="https://seedlings-ejp.openai.azure.com/",
        api_key="2cb70053536b4e1b8d76dfdb09ad2459",
        base_url=""
    )

    prompt = prompt.partial(
        tools=render_text_description(tools),
        tool_names=", ".join([t.name for t in tools]),
    )

    prompt.messages[0].prompt.template = role_prompt

    chat_model_with_stop = chat_model.bind(stop=["\nObservation"])

    # We need some extra steering, or the chat model forgets how to respond sometimes
    TEMPLATE_TOOL_RESPONSE = """TOOL RESPONSE: 
    ---------------------
    {observation}

    USER'S INPUT
    --------------------

    Okay, so what is the response to my last comment? If using information obtained from the tools you must mention it explicitly without mentioning the tool names - I have forgotten all TOOL RESPONSES! Remember to respond with a markdown code snippet of a json blob with a single action, and NOTHING else - even if you just want to respond to the user. Do NOT respond with anything except a JSON snippet no matter what!"""

    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_log_to_messages(
                x["intermediate_steps"], template_tool_response=TEMPLATE_TOOL_RESPONSE
            ),
            "chat_history": lambda x: x["chat_history"],
        }
        | prompt
        | chat_model_with_stop
        | JSONAgentOutputParser()
    )

    agent_executor = AgentExecutor(
        agent=agent, tools=tools, verbose=True, memory=memory
    )

    return agent_executor.invoke({"input": input})["output"]


def chat_with_intent(input: str, history: list, prompt: str, knowledge_base_id: int):
    intent = predict_intent(input, history[-10:])
    if intent["output"] == "W" or intent["output"] == "E":
        return ""
    else:
        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
        for message in history:
            if message.role == "user":
                memory.chat_memory.add_user_message(message.content)
            else:
                memory.chat_memory.add_ai_message(message.content)

        return chat(input, memory, prompt, knowledge_base_id)
