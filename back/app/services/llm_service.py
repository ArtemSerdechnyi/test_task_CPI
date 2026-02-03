from openai import AsyncOpenAI

from back.app.prompts.prompts import SYSTEM_MESSAGE, AI_ANALYST_USER_TEMPLATE
from back.app.schemas.valuation import AIPromptSchema


class LLMService:
    def __init__(self, api_key: str, model: str):
        self._model = model
        self._client = AsyncOpenAI(api_key=api_key)

    async def get_llm_analysis(self, finance_data: AIPromptSchema) -> str:
        populated_main_prompt = self.format_main_prompt(finance_data)
        template_messages = self.format_messages_payload(
            system_prompt=SYSTEM_MESSAGE, main_prompt=populated_main_prompt
        )
        llm_response = await self.gpt_request(template_messages=template_messages)

        return llm_response

    async def gpt_request(self, template_messages: list[dict[str, str]]) -> str:
        llm_response = await self._client.chat.completions.create(
            model=self._model,
            messages=template_messages,
        )

        return llm_response.choices[0].message.content

    @staticmethod
    def format_main_prompt(data: AIPromptSchema) -> str:
        return AI_ANALYST_USER_TEMPLATE.format(**data.model_dump())

    @staticmethod
    def format_messages_payload(system_prompt: str, main_prompt: str):
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": main_prompt},
        ]
