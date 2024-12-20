import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to crawl job listings
def crawl_jobs(base_url, max_pages=5):
    jobs = []  # To store job data

    for page in range(1, max_pages + 1):
        # Construct the URL for pagination
        url = f"{base_url}?page={page}"
        print(f"Crawling page: {url}")

        # Send GET request to the webpage
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch {url}")
            break

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all job cards
        job_cards = soup.find_all('div', class_='job-card')  # Adjust class name if needed

        for card in job_cards:
            try:
                # Extract job title
                title_tag = card.find('a', class_='job-title')
                job_title = title_tag.text.strip()
                job_link = title_tag['href']

                # Extract job location
                location_tag = card.find('span', class_='job-location')  # Adjust class name if needed
                job_location = location_tag.text.strip() if location_tag else "Not specified"

                # Extract company name
                company_tag = card.find('div', class_='job-company')  # Adjust class name if needed
                company_name = company_tag.text.strip() if company_tag else "Not specified"

                # Store the job details in a dictionary
                jobs.append({
                    'Title': job_title,
                    'Company': company_name,
                    'Location': job_location,
                    'Link': f"https://www.talenten.vn{job_link}"
                })
            except Exception as e:
                print(f"Error extracting job details: {e}")
                continue

    return jobs

# Main function
if __name__ == "__main__":
    base_url = "https://www.talenten.vn/en/jobs"
    max_pages = 3  # Adjust the number of pages to crawl

    # Crawl the job data
    job_data = crawl_jobs(base_url, max_pages)

    # Save to a CSV file
    df = pd.DataFrame(job_data)
    df.to_csv("jobs.csv", index=False)
    print(f"Saved {len(job_data)} job listings to jobs.csv")
