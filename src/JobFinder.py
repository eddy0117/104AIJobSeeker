import time
import random
import requests
import json
import logging
from .agents import (OptionAgent,
                      AnswerAgent, 
                      SimpleFilterAgent,
                      JobcatAgent)
from .utils.config import load_proxies, load_json

class JobFinder:
    def __init__(self, 
                 api_key=""):

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'Referer': 'https://www.104.com.tw/jobs/search/',
        }

        self.sort_dict = {
            '符合度': '1',
            '日期': '2',
            '經歷': '3',
            '學歷': '4',
            '應徵人數': '7',
            '待遇': '13',
        }


        prompt_file_dict = {
            'answer_prompt': "src/prompts/answer_prompt.txt",
            'option_prompt': "src/prompts/option_prompt_v3.txt",
            'simple_filter_prompt': "src/prompts/simple_filter_prompt.txt",
            'jobcat_prompt': "src/prompts/jobcat_prompt_v2.txt",
            }
        
        prompts_dict = self.load_prompts(prompt_file_dict)

        self.answer_agent = AnswerAgent(api_key, model="gpt-4o", base_prompt=prompts_dict['answer_prompt'])
        self.option_agent = OptionAgent(api_key, model="gpt-4o", base_prompt=prompts_dict['option_prompt'])
        self.simple_filter_agent = SimpleFilterAgent(api_key, model="gpt-4o", base_prompt=prompts_dict['simple_filter_prompt'])
        self.jobcat_agent = JobcatAgent(api_key, model="gpt-4o", base_prompt=prompts_dict['jobcat_prompt'])
        
        self.proxies = load_proxies('src/json/proxy.json')
        self.all_jobcat_dict = load_json('src/json/jobcat_dict.json', encoding='utf-8')

    def load_prompts(self, prompt_file_dict):
        prompts = {}
        for key, file_path in prompt_file_dict.items():
            with open(file_path, 'r', encoding='utf-8') as f:
                prompts[key] = f.read()
        return prompts

    def request_get(self, headers, url, params=None):
        "return a json data if success, otherwise None"
        # 若代理池有值則隨機選擇一個代理設定給 requests
        proxy = random.choice(self.proxies) if self.proxies else None
        proxies = {"http": proxy} if proxy else None
        r = requests.get(url, params=params, headers=headers, proxies=proxies)
        if r.status_code != requests.codes.ok:
            print('請求失敗', r.status_code)
            data = r.json()
            print(data['status'], data['statusMsg'], data['errorMsg'])
            return None
        return r.json()

    def search_job(self, keyword, max_mun=10, filtered_params=None, sort_type='符合度', is_sort_asc=False):
        jobs = []

        url = 'https://www.104.com.tw/jobs/search/list'
        query = f"jobsource=joblist_search&keyword={keyword}"

        if filtered_params:
            # 加上篩選參數，要先轉換為 URL 參數字串格式
            query += ''.join([f'&{key}={value}' for key, value, in filtered_params.items()])
        
        sort_params = f"&order={self.sort_dict.get(sort_type, '1')}"
        sort_params += '&asc=1' if is_sort_asc else '&asc=0'
        query += sort_params
        page = 1
        while len(jobs) < max_mun:
            # 逐頁迭代
            params = f'{query}&page={page}'
            data = self.request_get(self.headers, url, params)
            if not data:
                break
            total_count = data['data']['totalCount']
            jobs.extend(data['data']['list'])

            if (page == data['data']['totalPage']) or (data['data']['totalPage'] == 0):
                break
            page += 1
            time.sleep(random.uniform(3, 5))

        return jobs[:max_mun]
    
    
    
    def get_job_detail(self, jobs, filtered=True):

        t0 = time.time()
        result = []
        for job in jobs:
            job_page_uid = job['link']['job'].split('/')[-1].split('?')[0]
            job_uid = job['jobNo']
            page_content_url = f"https://www.104.com.tw/job/ajax/content/{job_page_uid}"

            data = self.request_get(self.headers, page_content_url)
            if not data:
                continue
            if filtered:
                result.append(self.filter_detail(data['data'], job['link']['job']))
            else:
                result.append(data['data'])
            # time.sleep(random.uniform(3, 5))
        print(f"共取得 {len(result)} 筆職缺資料, 耗時 {time.time()-t0:.2f} 秒")
        return result
    

    def filter_detail(self, job_detail, job_link):
        # 回傳求職者實際需要的資訊
        filtered_content = {
            'job_link': job_link.replace('//', ''),
            'job_name': job_detail.get('header', {}).get('jobName', ''),          # 職缺名稱
            'company_name': job_detail.get('header', {}).get('custName', ''),        # 公司名稱
            'appear_date': job_detail.get('header', {}).get('appearDate', ''),       # 上架日期
            'job_description': job_detail.get('jobDetail', {}).get('jobDescription', ''),  # 職缺描述
            'salary': job_detail.get('jobDetail', {}).get('salary', ''),             # 待遇
            'address': job_detail.get('jobDetail', {}).get('addressRegion', '') + 
                       job_detail.get('jobDetail', {}).get('addressDetail', ''),      # 工作地點
            'welfare': job_detail.get('welfare', {}).get('welfare', ''),             # 福利說明
        }

        languages_list = job_detail.get('condition', {}).get('language', [])

        job_condition = {
            'work_experience': job_detail.get('condition', {}).get('workExp', ''),     
            'education': job_detail.get('condition', {}).get('edu', ''),           
            'majors': job_detail.get('condition', {}).get('major', []),    
            'languages': [{'lang': lang.get('language', ''),
                           'listening': lang.get('ability', {}).get('listening', ''),
                           'speaking': lang.get('ability', {}).get('speaking', ''),
                           'reading': lang.get('ability', {}).get('reading', ''),
                           'writing': lang.get('ability', {}).get('writing', ''),} for lang in languages_list],
            'specialtys': [specialty.get('description', '') for specialty in job_detail.get('condition', {}).get('specialty', [])], 
            'skills': [skill.get('description', '') for skill in job_detail.get('condition', {}).get('skill', [])], 
            'other': job_detail.get('condition', {}).get('other', ''), 
        }

        filtered_content.update(job_condition)

        return filtered_content
    
   

    def find_job(self, filtered_params, user_prompt=None, keyword='', return_amount=20):
        """搜尋職缺"""
        jobs = self.search_job(keyword=keyword, max_mun=return_amount, filtered_params=filtered_params)
        logging.info(f"使用一般搜尋共找到 {len(jobs)} 筆職缺")
        if len(jobs) == 0:
            return None, None
        
        # jobs_detail = self.get_job_detail(jobs, filtered=True)
        # response = self.answer_agent.ask_for_job(jobs_detail, user_prompt, return_amount=return_amount)
        return [[job['jobName'], job['custName'], job['link']['job']] for job in jobs]
        
    def search_company(self, companys):
        """
        return company info:
        'name': 公司名稱,
        'uid': 公司編號
        """
        company_infos = []
        logging.info(f"正在尋找 {len(companys)} 間公司")
        for company in companys:
            company_info = self._search_company(company)
            if company_info:
                logging.info(f"名稱: {company_info['name']}, UID: {company_info['uid']}")
                company_infos.append(company_info)
        
        return company_infos
    
    def _search_company(self, company_keyword):
        # TODO: 改為使用 google 搜尋 "{company_keyword} site:104.com.tw"
        company_info = {}

        url = f"https://www.104.com.tw/company/ajax/list"
        params = f"keyword={company_keyword}&jobsource=n_my104_search&mode=s&page=1"
        data = self.request_get(self.headers, url, params)
        if not data:
            return None
        company_data = data['data'][0] # 取得第一筆資料
        company_info['name'] = company_data.get('name', '')
        company_info['uid'] = company_data.get('encodedCustNo', '')
        
        return company_info
    
    def search_company_job(self, company_info, keyword):
        
        company_job = []
        
        page = 1
        url = f"https://www.104.com.tw/company/ajax/joblist/{company_info['uid']}"
        params = f"job={keyword}&page={page}&pageSize=20&order=99&asc=0"
        data = self.request_get(self.headers, url, params)
        total_count = data['data']['totalCount']
        logging.info(f"從 {company_info['name']} 找到 {total_count} 筆職缺")
        while len(company_job) < total_count:
            params = f"job={keyword}&page={page}&pageSize=100&order=99&asc=0"
            data = self.request_get(self.headers, url, params)
            if not data:
                return None
            total_count = data['data']['totalCount']
            company_job_data = data['data'].get('list', [])['topJobs']
            company_job_data.extend(data['data'].get('list', [])['normalJobs'])
            if not company_job_data:
                return None
            
            company_job.extend([self.filter_company_job(job_data, idx) for idx, job_data in enumerate(company_job_data)])
            page+=1

        return company_job

    def filter_company_job(self, company_job_data, idx):
        filtered_content = {
            'idx': idx,
            'job_name': company_job_data.get('jobName', ''),
            # 'job_url': company_job_data.get('jobUrl', ''),
            'edu': company_job_data.get('edu', ''),
            # 'jd': company_job_data.get('jobDescription', ''),
            'jobexp': company_job_data.get('periodDesc', ''),
        }
        return filtered_content
    
    def search_company_job_option(self, company_info):
        """搜尋公司 option filter 選項"""
        # TODO: 兼職、全職要分開
        url = f"https://www.104.com.tw/company/ajax/joblist/options/{company_info['uid']}"
        data = self.request_get(self.headers, url)
        if not data:
            return None
        all_role_jobcat = data['data']['roleJobCat']
        all_role_jobcat_dict = {}
        for k, v in all_role_jobcat.items():
            if k in ["0_0", "1_0"]: # 跳過 "職務類別(不拘)" 和 "全職-職務類別(不拘)"
                continue
            if len(v.split('-')) > 1: # 有些公司可能沒有全職-兼職的區分
                (role, jobcat) = v.split('-')
                if role == '0': # 跳過兼職
                    continue
                all_role_jobcat_dict[jobcat] = k
            else:
                all_role_jobcat_dict[v] = k
        return all_role_jobcat_dict

    def search(self, user_prompt):
        """搜尋職缺"""
        jobcat_list = self.jobcat_agent.ask_agent(user_prompt=user_prompt)
        if not jobcat_list:
            logging.info("搜尋失敗，請檢查輸入的條件")
            return None
        jobcat_list = jobcat_list['jobcat']

        filtered_params, search_opts = self.option_agent.ask_for_option(user_prompt=user_prompt)
        filtered_params['jobcat'] = ','.join(jobcat_list)
        
        filtered_jobcat_list = []
        for jobcat in jobcat_list:
            filtered_jobcat_list.append(self.all_jobcat_dict[jobcat])

        logging.info(f"company: {search_opts['company']}")
        logging.info(f"jobcat: {filtered_jobcat_list}")
        logging.info(f"篩選條件: {filtered_params}")

        company_infos = self.search_company(search_opts['company'])
        if len(company_infos) > 0:
            for company_info in company_infos:
                # 取得公司職缺
                company_role_jobcat = self.search_company_job_option(company_info)
                paired_jobcats = [company_role_jobcat[cat] for cat in filtered_jobcat_list if cat in company_role_jobcat]
                if not paired_jobcats:
                    # 沒有找到與使用者相關的職務類別
                    continue
                logging.info(f"{paired_jobcats}")
                logging.info(list(filter(lambda x: x in company_role_jobcat, filtered_jobcat_list)))
                # all_company_jobs = self.search_company_job(company_info, keyword='')
                # logging.info(f"從 {company_info['name']} 找到 {len(all_company_jobs)} 筆職缺")
        return None
        # return self.find_job(filtered_params=filtered_params, keyword='')


        all_company_jobs = {}
        filter_params, search_opt_dict = self.option_agent.ask_for_option(user_prompt)
        if not filter_params:
            logging.info("搜尋失敗，請檢查輸入的條件")
            return None

        logging.info(f"篩選條件: {search_opt_dict}")
        companys = search_opt_dict.get('company', [])
        keyword = search_opt_dict.get('keyword', '')
        
        if len(companys) > 0:
            # 先搜尋公司")
            company_infos = self.search_company(companys)
            for company_info in company_infos:
                # 取得公司職缺
                all_company_jobs[company_info['name']] = self.search_company_job(company_info, keyword)
        
            company_job_index_dict = self.simple_filter_agent.ask_agent(user_prompt=user_prompt, content_prompt=str(all_company_jobs))

            for company_name, job_index_list in company_job_index_dict.items():
                # 取得公司職缺
                logging.info(f"從 {company_name} 濾除後找到 {len(job_index_list)} 筆職缺")
                all_company_jobs[company_name] = [all_company_jobs[company_name][idx] for idx in job_index_list]
        else:
            all_company_jobs, jobs_detail = self.find_job(user_prompt, filter_params, keyword=keyword)


        return all_company_jobs