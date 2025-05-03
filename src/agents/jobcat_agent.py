import json
import re
from langchain_core.output_parsers import JsonOutputParser

from ._base_agent import BaseAgent


class JobcatAgent(BaseAgent):
    def __init__(self, model, base_prompt):
        super().__init__(model, base_prompt)

    def ask_agent(self, user_prompt):
        res = self.call_openai_api(user_prompt=user_prompt)
        pattern = re.compile(r'({.*?})', re.DOTALL)
        match = pattern.search(res)
        if match:
            content = match.group(1)
            json_content = json.loads(content)
        else:
            return None
       

        return json_content

