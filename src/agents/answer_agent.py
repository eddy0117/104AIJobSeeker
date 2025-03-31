import re
import json
from ._base_agent import BaseAgent

class AnswerAgent(BaseAgent):
    # 修正建構子名稱
    def __init__(self, api_key, model, base_prompt):
        super().__init__(api_key, model, base_prompt)
        # 若需要共用設定，可視需求移至 utils/config 載入
        self.option_dict = None
        with open("src/json/option_map.json", 'r', encoding='utf-8') as f:
            self.option_dict = json.load(f)

    def ask_for_job(self, jobs_detail, user_prompt, return_amount=10):
        amount_prompt = f"最後返回{str(return_amount)}筆資料。\n"
        answer = self.call_openai_api(amount_prompt + str(jobs_detail), user_prompt)
        return answer
