import requests
import html2text
import os
from dotenv import load_dotenv
from openai import OpenAI
from selenium import webdriver
import asyncio
from playwright.async_api import async_playwright
import time

from schemas.job import Job, JobList

load_dotenv()

async def crawl_and_extract(url):
  async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    page = await browser.new_page()

    # Navigate to the URL
    await page.goto(url)
    content = await page.content()  # Get the page content
    await browser.close()

  # Extract information using OpenAI
  openAIClient = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
  response = openAIClient.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[
      {"role": "system", "content": "You are an expert at structured data extraction. You will be given a pages content of a jobs hiring website, you should extract all the jobs available."},
      {"role": "user", "content": f"Extract useful information from this HTML: {content}"}
    ],
    response_format=JobList,
  )

  extracted_info = response.choices[0].message.parsed
  print(extracted_info)
  return extracted_info

def send_data_to_api(crawled_data):
  try:
    requestBody = {
      "data": crawled_data
    }

    # Send each data entry to the API
    headers = {
      "Content-Type": "application/json",
      "x-key-conjure": os.environ['CONJURE_API_KEY']
    }
    response = requests.post(os.environ['CONJURE_API_URL'], json=requestBody, headers=headers)
    if response.status_code == 200:
      print(f"Successfully sent data to API: {response.text}")
    else:
      print(f"Failed to send data: {response.status_code}, {response.text}")

  except Exception as e:
    print(f"Error sending data to API: {e}")

def crawl_job_list_with_selenium(url):
  driver = webdriver.Chrome()  # Ensure you have ChromeDriver installed
  driver.get(url)
  time.sleep(3)
  html_content = driver.page_source
  driver.quit()

  h = html2text.HTML2Text()
  web_content = h.handle(str(html_content))

  openAIClient = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
  job_list = openAIClient.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[
      {
        "role": "system",
        "content": f"You are an expert at structured data extraction. You will be given a pages content of a jobs hiring website, you should extract all the jobs available.",
      },
      {"role": "user", "content": web_content},
    ],
    response_format=JobList,
  )

  return job_list.choices[0].message.parsed

def crawl_job_detail_with_selenium(base_url, job_list):
  jobs = []

  for job in job_list.jobs:
    try:
      job_detail_url = f"{base_url}{job.job_url}"
      print(job_detail_url)

      driver = webdriver.Chrome()  # Ensure you have ChromeDriver installed
      driver.get(job_detail_url)
      time.sleep(3)
      html_content = driver.page_source
      driver.quit()

      print(html_content)

      h = html2text.HTML2Text()
      web_content = h.handle(str(html_content))

      print(web_content)

      openAIClient = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
      crawled_job = openAIClient.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"You are an expert at structured data extraction. You will be given a pages content of a jobs hiring website, you should extract job information from job detail based on the schema without translate the original content. Also return a field 'position_appeal' will be the charm of job position. The job position appeal is the most attractive feature of the job position. It is the reason why a candidate would want to apply for the job. The position appeal should be extracted from the job detail page. The position appeal should be a short sentence that describes the most attractive feature of the job position.",
            },
            {"role": "user", "content": web_content},
        ],
        response_format=Job,
      )

      job_detail = crawled_job.choices[0].message.parsed
      jobs.append({
        "title": job.job_title,
        "detail_url": job.job_url,
        "detail": job_detail.model_dump_json()
      })
    except Exception as e:
      print(f"Error extracting job details: {e}")
      continue

  return {
    'jobs': jobs
  }

async def start_crawl(urls):
  print(urls)
  tasks = [crawl_and_extract(url) for url in urls]
  results = await asyncio.gather(*tasks)
  return results

# Main function
# if __name__ == "__main__":
#   base_url = "https://agent.herp.cloud"
# # "urls": ["https://agent.herp.cloud/p/wn1kW5tvuVnPrFUClJQdbN8-JLIpvkVpKdrhOdy0Xa0"]
#   import sys
#   import json
#   # urls = json.loads(sys.argv[1])
#   urls = [f"{base_url}/p/wn1kW5tvuVnPrFUClJQdbN8-JLIpvkVpKdrhOdy0Xa0"]
#   extracted_data = asyncio.run(main(urls))
#   jobs = extracted_data[0].jobs

#   print([job.model_dump_json() for job in jobs])

#   result = [job.model_dump_json() for job in jobs]

  # print(json.dumps(json.dumps(job) for job in extracted_data[0].jobs))

  # job_list = crawl_job_list_with_selenium(f"{base_url}/p/wn1kW5tvuVnPrFUClJQdbN8-JLIpvkVpKdrhOdy0Xa0")

  # job_list_with_detail = crawl_job_detail_with_selenium(base_url, job_list)
  # print(job_list_with_detail)

  # send_data_to_api(job_list_with_detail)
