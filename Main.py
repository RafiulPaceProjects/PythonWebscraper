# Importing necessary modules
import requests
from bs4 import BeautifulSoup
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from langdetect import detect
import pandas as pd
import time

# Function to fetch the HTML content of a webpage
def fetch_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    return None

# Function to transliterate text if it is in Bengali
def transliterate_if_bengali(text):
    if detect(text) == 'bn':
        return transliterate(text, sanscript.BENGALI, sanscript.ITRANS)
    return text

# Function to parse job details from BD Jobs
def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")
    job_listings = soup.find_all("div", class_="featured-job")

    job_data = []
    for job in job_listings:
        try:
            title_element = job.find("div", class_="title").find("a")
            title = title_element.get_text(strip=True) if title_element else "N/A"

            company_element = job.find("div", class_="company")
            company = company_element.get_text(strip=True) if company_element else "N/A"

            location_element = job.find("div", class_="loccal").find("p")
            location = location_element.get_text(strip=True) if location_element else "N/A"

            experience_element = job.find("div", class_="exp loccal").find("p")
            experience = experience_element.get_text(strip=True) if experience_element else "N/A"

            deadline_element = job.find("p", class_="dt").find("strong")
            deadline = deadline_element.get_text(strip=True) if deadline_element else "N/A"

            education_element = job.find("div", class_="education")
            education = education_element.find("li").get_text(strip=True) if education_element else "N/A"

            job_link_element = job.find("div", class_="title").find("a", href=True)
            job_link = f"https://jobs.bdjobs.com/{job_link_element['href']}" if job_link_element else "N/A"

            job_data.append({
                "Title": transliterate_if_bengali(title),
                "Company": transliterate_if_bengali(company),
                "Location": transliterate_if_bengali(location),
                "Experience": transliterate_if_bengali(experience),
                "Deadline": transliterate_if_bengali(deadline),
                "Education": transliterate_if_bengali(education),
                "Job Link": job_link,
            })

        except AttributeError as e:
            print(f"Error extracting job data: {e}")
            print(f"Job HTML: {job.prettify()}")

    return job_data

# Function to scrape multiple pages
def scrape_bd_jobs(pages=5):
    base_url = "https://jobs.bdjobs.com/jobsearch.asp?log=stats&pg="
    all_jobs = []

    for page in range(1, pages + 1):
        print(f"Scraping page {page}...")
        html = fetch_page(base_url + str(page))
        if html:
            jobs = parse_html(html)
            all_jobs.extend(jobs)
        else:
            print(f"Failed to retrieve page {page}")
        time.sleep(2)  # Avoid overwhelming the server

    return all_jobs

# Main execution
if __name__ == "__main__":
    job_data = scrape_bd_jobs(pages=5)  # Scrape first 5 pages

    # Convert data to DataFrame
    df = pd.DataFrame(job_data)

    # Save to Excel
    df.to_excel("bd_jobs_fixed.xlsx", index=False)

    print("Data successfully saved to bd_jobs_fixed.xlsx")