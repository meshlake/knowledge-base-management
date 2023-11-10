from datetime import datetime
import logging
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
import os
from dotenv import load_dotenv
import json

load_dotenv()



def is_answer_successful(question:str, answer: str):
    # os.environ["OPENAI_API_TYPE"] = "azure"
    # os.environ["OPENAI_API_BASE"] = os.getenv("AZURE_OPENAI_API_BASE")
    # os.environ["OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
    # os.environ["OPENAI_API_VERSION"] = "2023-05-15"
    llm = ChatOpenAI()
    prompt_template = PromptTemplate.from_template(
        "判断下面这段问答中的答案是否表示一个成功的回答并给出理由，```question:{question}``` ```answer:{answer}```"
    )
    prompt = prompt_template.format(
        question=question,
        answer=answer,
    )
    template = """
    你负责判断给你的一段问答中的答案是否表示一个成功的回答并给出理由。
    你的返回应该是一段json, 
    例如：{{is_success: 是否表达相似的含义,布尔值, reason: 你的理由}}
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