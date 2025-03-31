import json
import re
from ._base_agent import BaseAgent
from ..utils.config import load_json   # 新增工具函數引入

class OptionAgent(BaseAgent):
    # 如有需要，可擴充 AnswerAgent 特有功能
    def __init__(self, api_key, model, base_prompt):
        super().__init__(api_key, model, base_prompt)
        # 改用 utils/config 載入 option_map.json
        self.option_dict = load_json("src/json/option_map.json", encoding='utf-8')

    def ask_for_option(self, user_prompt):
        filtered_params = {}
        res = self.call_openai_api(user_prompt=user_prompt)
        pattern = re.compile(r'({.*?})', re.DOTALL)
        match = pattern.search(res)
        if match:
            content = match.group(1)
            json_content = json.loads(content)
        else:
            return None, None
        for k, v in json_content.items():
            if k not in ["area", "edu", "jobexp"] or v == '':
                continue
            if isinstance(v, list):
                filtered_params[k] = ','.join([self.option_dict[k][i] for i in v])
            else:
                filtered_params[k] = self.option_dict[k][v]

        return filtered_params, json_content

