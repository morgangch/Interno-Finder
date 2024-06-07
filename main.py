from bs4 import BeautifulSoup
import requests
import re
import json
import os
import time
import random
import sys
import traceback
import urllib.parse

# 0. Constants
area = "Occitanie"
country = "France"
job = "stage informatique"
job_type = "Stage"
job_query = job.replace(" ", "+")
# 0.1. Get the list of all the URLs
# Notes : Hellowork page switch only needs one new arg in post req : &p=PageNumber. If out of range, it returns an empty offer list.
# Jooble page is an infinite scrollable page. &p arg seems to have no effect. It returns a list of offers, but the list is always the same.
urls = {}

# 1. Define some functions
def get_consts():
    area = input("Area: ")
    job = input("Job: ")
    job_type = input("Job type: ")
    job_query = job.replace(" ", "+")
    return area, job, job_type, job_query

def build_urls(area, job, job_type, job_query):
    urls = {
        f'https://www.hellowork.com/fr-fr/emploi/recherche.html?k={job_query}&k_autocomplete=&l={area}&l_autocomplete=http%3A%2F%2Fwww.rj.com%2Fcommun%2Flocalite%2Fregion%2F76&c={job_type}&d=all': "HelloWork",
        f'https://fr.jooble.org/SearchResult?p=6&rgns={area}&ukw={job.replace(" ", "%20")}' : "Jooble",
        f"https://www.studentjob.fr/offre?region_name=&job_guide_name=&search%5Bzipcode_eq%5D={area}&search%5Bkeywords_scope%5D={job_query}&sort_by=relevancy&search%5Bjob_types%5D%5Bid%5D%5B%5D=6": "StudentJob",
        f"https://jobs.smartrecruiters.com/?keyword={job} {area}" : "SmartRecruiters",
        f"https://www.welcometothejungle.com/en/jobs?refinementList%5Boffices.country_code%5D%5B%5D=FR&refinementList%5Boffices.state%5D%5B%5D=Occitanie&query=stage%20informatique&page=1&aroundQuery=Occitanie%2C%20France": "WelcomeToTheJungle"
    }
    return urls

def change_elt_in_url(url, elt, new_val):
    url_parts = urllib.parse.urlparse(url)
    query = url_parts.query
    query_dict = urllib.parse.parse_qs(query)
    query_dict[elt] = new_val
    query = urllib.parse.urlencode(query_dict, doseq=True)
    url = urllib.parse.urlunparse((url_parts.scheme, url_parts.netloc, url_parts.path, url_parts.params, query, url_parts.fragment))
    return url

if __name__ == "__main__":
    # 2. Scrape the URLs
    if int(input("Do you want to change the constants ? (0/1) :\n")) == 1:
        area, job, job_type, job_query = get_consts()
    urls = build_urls(area, job, job_type, job_query)
    for url in urls.keys():
        print(f"Scraping {url} : {urls[url]}...")
        if urls[url] == "HelloWork":
            page_number = 1
            while True:
                print(f"Page {page_number}")
                url = change_elt_in_url(url, "p", page_number)
                print(url)
                page = requests.get(url)
                soup = BeautifulSoup(page.content, 'html.parser')
                offers = soup.find_all("div", class_="offer")
                if len(offers) == 0:
                    break
                for offer in offers:
                    print(offer.find("a", class_="offer-title").get_text())
                page_number += 1
        elif urls[url] == "Jooble":
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            offers = soup.find_all("div", class_="vacancy_wrapper")
            for offer in offers:
                print(offer.find("a", class_="link-position").get_text())
        elif urls[url] == "StudentJob":
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            offers = soup.find_all("div", class_="job-listing")
            for offer in offers:
                print(offer.find("a", class_="job-title").get_text())
        elif urls[url] == "SmartRecruiters":
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            offers = soup.find_all("div", class_="job-listing")
            for offer in offers:
                print(offer.find("a", class_="job-title").get_text())
        elif urls[url] == "WelcomeToTheJungle":
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            offers = soup.find_all("div", class_="sc-dnqmqq")
            for offer in offers:
                print(offer.find("a", class_="sc-gisBJw").get_text())
        print("Done.")
