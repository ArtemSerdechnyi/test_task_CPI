from openai import OpenAI

from back.app.core.config import settings
from back.app.prompts.prompts import (
    SYSTEM_MESSAGE, 
    AI_ANALYST_USER_TEMPLATE
)
from back.app.schemas.valuation import AIPromptSchema


class LLMService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def get_llm_analysis(self, finance_data: AIPromptSchema) -> str:
        populated_main_prompt = self.format_main_prompt(finance_data)
        template_messages = self.format_messages_payload(
            system_prompt=SYSTEM_MESSAGE, main_prompt=populated_main_prompt
        )
        llm_response = self.gpt_request(template_messages=template_messages)

        return llm_response

    def gpt_request(self, template_messages: list[dict[str, str]]) -> str:
        llm_response = self.openai_client.responses.create(
            model=settings.LLM,
            input=template_messages,
        )

        return llm_response.output[0].content[0].text

    @staticmethod
    def format_main_prompt(data: AIPromptSchema) -> str:
        return AI_ANALYST_USER_TEMPLATE.format(**data.model_dump())

    @staticmethod
    def format_messages_payload(system_prompt: str, main_prompt: str):
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": main_prompt},
        ]
