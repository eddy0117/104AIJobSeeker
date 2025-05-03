import openai
import logging
from langchain_openai import ChatOpenAI

class BaseAgent:
    def __init__(self, model, base_prompt):
        
        self.model = ChatOpenAI(model=model)
        self.base_prompt = base_prompt

    def call_openai_api(self, content_prompt="", user_prompt=""):
        try:
            logging.info("calling ChatGPT API...")
            response = openai.chat.completions.create(
                model=self.model,
                max_tokens=10000,
                messages=[
                    {"role": "system", "content":  content_prompt + "\n" + self.base_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0,
            )
            extracted_text = response.choices[0].message.content.strip()
            return extracted_text
        except Exception as e:
            logging.error(f"Error when calling ChatGPT API: {e}")
            return None
