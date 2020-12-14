from logging import log
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium import webdriver
import time
import pandas as pd
from selenium.webdriver.remote.remote_connection import LOGGER
import json


def get_jobs(keyword, num_jobs, verbose, driver_path, sleep):
    '''Gathers jobs as a dataframe, scraped from Glassdoor'''

    # Initializing the webdriver
    options = webdriver.ChromeOptions()

    # Change the path to where chromedriver is in your home folder.
    driver = webdriver.Chrome(executable_path=driver_path, options=options)

    driver.set_window_size(1120, 1000)

    driver.get(
        ("https://www.glassdoor.com/Job/jobs.htm?suggestCount=0&suggestChosen=false&clickSource=searchBtn&typedKeyword=" +
         keyword+"&sc.keyword="+keyword+"&locT=&locId=&jobType="))

    jobs = []

    def xpathHandler(path):
        try:
            return driver.find_element_by_xpath(path).text
        except NoSuchElementException:
            return -1

            # If true, should be still looking for new jobs.
    while len(jobs) < num_jobs:

        # Let the page load. Change this number based on your internet speed.
        # Or, wait until the webpage is loaded, instead of hardcoding it.
        time.sleep(sleep)

        # Test for the "Sign Up" prompt and get rid of it.
        try:
            driver.find_element_by_class_name("selected").click()
        except ElementClickInterceptedException:
            pass

        time.sleep(.1)

        # clicking to the X.
        try:
            driver.find_element_by_css_selector('[alt="Close"]').click()
            print('x out worked')
        except NoSuchElementException:
            print('x out failed')
            pass

        # Going through each job in this page
        # jl for Job Listing. These are the buttons we're going to click.
        job_buttons = driver.find_elements_by_class_name("jl")

        for job_button in job_buttons:

            if len(jobs) == num_jobs:
                break

            job_button.click()  # You might

            time.sleep(1)

            job_info = {}

            job_info.update({'company_name': xpathHandler(
                './/div[@class="employerName"]')})

            job_info.update({'location': xpathHandler(
                './/div[@class="location"]')})

            job_info.update({'job_title': xpathHandler(
                './/div[contains(@class, "title")]')})

            job_info.update({'job_description': xpathHandler(
                './/div[@class="jobDescriptionContent desc"]')})

            job_info.update({'salary_estimate': xpathHandler(
                './/div[@class="salary"]//span')})

            job_info.update(
                {'rating': xpathHandler('.//span[@class="rating"]')})

            # Printing for debugging
            if verbose:
                print(json.dumps(job_info, indent=1))

            company = {}

            try:
                # Going to the Company tab
                driver.find_element_by_xpath(
                    './/div[@class="tab" and @data-tab-type="overview"]').click()

                company.update({'headquarters': xpathHandler(
                    './/div[@class="infoEntity"]//label[text()="Headquarters"]//following-sibling::*')})

                company.update({'size': xpathHandler(
                    './/div[@class="infoEntity"]//label[text()="Size"]//following-sibling::*')})

                company.update({'founded': xpathHandler(
                    './/div[@class="infoEntity"]//label[text()="Founded"]//following-sibling::*')})

                company.update({'type_of_ownership': xpathHandler(
                    './/div[@class="infoEntity"]//label[text()="Type"]//following-sibling::*')})

                company.update({'industry': xpathHandler(
                    './/div[@class="infoEntity"]//label[text()="Industry"]//following-sibling::*')})

                company.update({'sector': xpathHandler(
                    './/div[@class="infoEntity"]//label[text()="Sector"]//following-sibling::*')})

                company.update({'revenue': xpathHandler(
                    './/div[@class="infoEntity"]//label[text()="Revenue"]//following-sibling::*')})

                company.update({'competitors': xpathHandler(
                    './/div[@class="infoEntity"]//label[text()="Competitors"]//following-sibling::*')})

           # Rarely, some job postings do not have the "Company" tab.
            except NoSuchElementException:
                company.update({'headquarters': -1})
                company.update({'size': -1})
                company.update({'founded': -1})
                company.update({'type_of_ownership': -1})
                company.update({'industry': -1})
                company.update({'sector': -1})
                company.update({'revenue': -1})
                company.update({'competitors': -1})

            if verbose:
                print(json.dumps(company, indent=1))

            # add job to jobs
            jobs.append({"Job Title": job_info['job_title'],
                         "Salary Estimate": job_info['salary_estimate'],
                         "Job Description": job_info['job_description'],
                         "Rating": job_info['rating'],
                         "Company Name": job_info['company_name'],
                         "Location": job_info['location'],
                         "Headquarters": company['headquarters'],
                         "Size": company['size'],
                         "Founded": company['founded'],
                         "Type of ownership": company['type_of_ownership'],
                         "Industry": company['industry'],
                         "Sector": company['sector'],
                         "Revenue": company['revenue'],
                         "Competitors": company['competitors']
                         })

            print("Progress: {0} / {1}".format(len(jobs), num_jobs))

        # Clicking on the "next page" button
        try:
            driver.find_element_by_xpath('.//li[@class="next"]//a').click()
        except NoSuchElementException:
            print("Scraping terminated before reaching target number of jobs. Needed {0}, got {1}.".format(
                num_jobs, len(jobs)))
            break

    # This line converts the dictionary object into a pandas DataFrame.
    return pd.DataFrame(jobs)
