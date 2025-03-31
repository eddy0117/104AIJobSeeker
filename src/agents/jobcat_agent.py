import json
import re
from ._base_agent import BaseAgent


class JobcatAgent(BaseAgent):
    # 如有需要，可擴充 AnswerAgent 特有功能
    def __init__(self, api_key, model, base_prompt):
        super().__init__(api_key, model, base_prompt)

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

