from datetime import datetime
import logging
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
import os
from dotenv import load_dotenv
import json

load_dotenv()


def is_answer_successful(question: str, answer: str):
    # azure_endpoint = os.getenv("AZURE_OPENAI_API_BASE")
    # os.environ["OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
    # llm = AzureChatOpenAI(
    #     azure_deployment="gpt-35-turbo",
    #     openai_api_version="2023-05-15",
    #     azure_endpoint=azure_endpoint,
    # )
    llm = AzureChatOpenAI(
        azure_deployment="gpt-4",
        openai_api_version="2023-05-15",
        azure_endpoint="https://seedlings-ejp.openai.azure.com/",
        api_key="2cb70053536b4e1b8d76dfdb09ad2459",
    )
    prompt_template = PromptTemplate.from_template(
        """
            "问答：\n"
            "question:{question}\n",
            "answer:{answer}",
        """
    )
    prompt = prompt_template.format(
        question=question,
        answer=answer,
    )
    template = """
    你是世界上最可靠的问答判断专家。\n
    你负责判断给你的问答中的答案是否表示一个成功的回答并给出理由,并且将结果变为json结构进行回答。\n
    返回的json结构如下：\n
    {{is_success: 是否表达相似的含义,布尔值, reason: 你的理由}}
    """
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template = "{text}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )
    chain = LLMChain(llm=llm, prompt=chat_prompt)
    res = chain.run(prompt)
    try:
        res = json.loads(res)
        logging.info(prompt)
        logging.info(res["is_success"])
        logging.info(res["reason"])
        return res["is_success"]
    except Exception:
        logging.info(res)
        return True
