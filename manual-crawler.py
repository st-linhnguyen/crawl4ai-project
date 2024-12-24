import requests
from bs4 import BeautifulSoup
import html2text
import pandas as pd
from dotenv import load_dotenv

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

# Main function
if __name__ == "__main__":
  base_url = "https://www.talenten.vn"
  max_pages = 2  # Adjust the number of pages to crawl

  # Crawl the job data
  job_data = crawl_jobs(base_url, max_pages)

  # Save to a CSV file
  df = pd.DataFrame(job_data)
  df.to_json("jobs.json", orient="records")
  print(f"Saved {len(job_data)} job listings to jobs.csv")
