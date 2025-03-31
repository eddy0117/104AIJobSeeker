import os
import logging
import yaml

from src.JobFinder import JobFinder


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():

    # Load configuration from YAML file
    if not os.path.exists("config.yaml"):
        with open("config.yaml", "w", encoding="utf-8") as file:
            yaml.dump({"api_key": None}, file)
        logging.error("config.yaml created. Please add your OpenAI API key.")
        return
    with open("config.yaml", "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    api_key = config["api_key"]
    job_finder = JobFinder(api_key)
    user_prompt = "幫我找金融業公司有關演算法或ai的工作，在台北新北或新竹"
    # response, jobs_detail = job_finder.find_job(user_prompt, return_amount=15)
    response = job_finder.search(user_prompt)
    print("Response:", response)


if __name__ == "__main__":
    main()
