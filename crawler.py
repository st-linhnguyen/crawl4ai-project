import requests
from bs4 import BeautifulSoup
import pandas as pd
import html2text
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

from schemas.job import Job, JobList

load_dotenv()

# Function to crawl job listings
def crawl_jobs(base_url, max_pages=5):
    jobs = []  # To store job data

    for page in range(max_pages):
        # Construct the URL for pagination
        url = f"{base_url}/en/jobs?page={page+1}"
        print(f"Crawling page: {url}")

        # Send GET request to the webpage
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch {url}")
            break

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all job cards
        job_cards = soup.find_all('li', class_='job-item')  # Adjust class name if needed

        for card in job_cards:
            try:
                # Extract job title
                title_tag = card.find('h4', class_='card-title')
                job_title = title_tag.text.strip()
                job_link = title_tag.find('a', class_='txt-link-dark-gray')["href"]

                job_detail_url=f"{base_url}{job_link}"
                job_detail = crawl_jobs_detail(job_detail_url)

                # Store the job details in a dictionary
                jobs.append({
                    'Title': job_title,
                    # 'Company': company_name,
                    # 'Location': job_location,
                    'Link': f"https://www.talenten.vn{job_link}",
                    'Detail': job_detail
                })
            except Exception as e:
                print(f"Error extracting job details: {e}")
                continue

    return jobs

def crawl_jobs_detail(job_detail_url):
  print(f"Crawling page: {job_detail_url}")
  h = html2text.HTML2Text()

  job_detail_response = requests.get(job_detail_url)
  if job_detail_response.status_code != 200:
      print(f"Failed to fetch {job_detail_url}")

  job_detail_soup = BeautifulSoup(job_detail_response.text, 'html.parser')

  job_detail_header = job_detail_soup.find('section', class_='job-detail-header')
  job_title = job_detail_header.find('h1', class_='txt-h3 mt-1 mb-2')
  job_company = job_detail_header.find('a', class_='fs-14 txt-link-dark-gray')
  job_location = job_detail_header.find('span', class_='ant-typography fs-14 css-imkqvq')

  job_description_section = job_detail_soup.find('section', class_='job-section section-job-description')
  job_description = h.handle(str(job_description_section))
  job_requirement_section = job_detail_soup.find('section', class_='job-section section-requirements')
  job_requirement = h.handle(str(job_requirement_section))
  job_benefit_section = job_detail_soup.find('section', class_='job-section section-benefits')
  job_benefit = h.handle(str(job_benefit_section))

  return {
    'Title': job_title.text.strip(),
    'Company': job_company.text.strip(),
    'Location': job_location.text.strip(),
    'Description': job_description,
    'Requirement': job_requirement,
    'Benefit': job_benefit
  }

def crawl_jobs_with_ai(url):
  print(os.environ['OPENAI_API_KEY'])
  openAIClient = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
  h = html2text.HTML2Text()

  response = requests.get(url)
  if response.status_code != 200:
    print(f"Failed to fetch {url}")

  web_content = h.handle(response.text)

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

  print(job_list)
  return job_list.choices[0].message.parsed


def crawl_job_detail_with_ai(url):
  openAIClient = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
  h = html2text.HTML2Text()

  response = requests.get(url)
  if response.status_code != 200:
    print(f"Failed to fetch {url}")

  web_content = h.handle(response.text)

  job_detail = openAIClient.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": f"You are an expert at structured data extraction. You will be given a pages content of a jobs hiring website, you should extract job information from job list and job detail based on the schema. Also return a field 'position_appeal' will be the charm of job position. The job position appeal is the most attractive feature of the job position. It is the reason why a candidate would want to apply for the job. The position appeal should be extracted from the job detail page. The position appeal should be a short sentence that describes the most attractive feature of the job position.",
        },
        {"role": "user", "content": web_content},
    ],
    response_format=Job,
  )
  return job_detail.choices[0].message.parsed


def send_data_to_api():
  data_file="jobs.json"

  try:
    # Load crawled data from file
    with open(data_file, "r") as f:
      crawled_data = json.load(f)

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

  except FileNotFoundError:
    print(f"File {data_file} not found. Ensure the crawler ran successfully.")
  except Exception as e:
    print(f"Error sending data to API: {e}")

# Main function
if __name__ == "__main__":
  base_url = "https://www.talenten.vn"
  max_pages = 2  # Adjust the number of pages to crawl

  # Crawl the job data
  # job_data = crawl_jobs(base_url, max_pages)

  # Save to a CSV file
  # df = pd.DataFrame(job_data)
  # df.to_json("jobs.json", orient="records")
  # print(f"Saved {len(job_data)} job listings to jobs.csv")

  # send_data_to_api()

  job_list = crawl_jobs_with_ai("https://agent.herp.cloud/p/wn1kW5tvuVnPrFUClJQdbN8-JLIpvkVpKdrhOdy0Xa0")
  print(job_list)
