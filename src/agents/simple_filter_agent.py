import json
import re
from ._base_agent import BaseAgent

class SimpleFilterAgent(BaseAgent):
    # 如有需要，可擴充 AnswerAgent 特有功能
    def __init__(self, api_key, model, base_prompt):
        super().__init__(api_key, model, base_prompt)


    def ask_agent(self, content_prompt="", user_prompt=""):
        filter_params = {}
        res = self.call_openai_api(content_prompt=content_prompt, user_prompt=user_prompt)
        res = res.replace("\n", "")
        pattern = re.compile(r'({.*?})', re.DOTALL)
        match = pattern.search(res)
        if match:
            content = match.group(1)
            json_content = json.loads(content)
        else:
            try:
                json_content = json.loads(res)
            except json.JSONDecodeError:
                print("沒有找到符合的 JSON 格式")
                return None
        return json_content

