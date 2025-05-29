import requests
from bs4 import BeautifulSoup
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_jobs(keyword=None,location_id=None):

    base_url="https://infopark.in/companies/job-search"

    if location_id:
        main_url="https://infopark.in/companies/job-search"+f'/{location_id}'
    else:
         main_url="https://infopark.in/companies/job-search"

    res=requests.get(main_url,verify=False)
    soup=BeautifulSoup(res.text,'lxml')

    pagination=soup.find('ul',{'class':'pagination'})
    last_page=1

    if pagination:
        page_no=[]
        for li in pagination.find_all('li'):
            try:    
                num=int(li.text.strip())
                page_no.append(num)
            except ValueError:
                continue
        last_page=max(page_no)

    all_links=[]
    for i in range(1,last_page+1):
        full_url=f"{main_url}?page={i}"
        all_links.append(full_url)          
    job_result=[]
    for i in all_links:
        res=requests.get(i,verify=False)
        soup=BeautifulSoup(res.text,'lxml')
        jobs=soup.find_all('div',{'class':'job-info-sec'})

        for job in jobs:
            table=job.find("table")
            if table:
                rows=table.find('tbody').find_all('tr')
                for row in rows:
                    columns=row.find_all('td')
                    job_title = columns[0].text.strip()
                    company_name=columns[1].text.strip()
                    last_date=columns[2].text.strip()
                    details_link = columns[3].find("a")["href"]

                    if last_date:
                        try:
                            parse_date= datetime.strptime(last_date,"%d %b %Y")
                        except Exception:
                            parse_date= datetime.min

                    
                    if keyword:
                        if keyword.lower() not in job_title.lower():
                            continue
                        else:
                            job_result.append({
                                'title':job_title,
                                'company':company_name,
                                'date':last_date,
                                'link':details_link,
                                'parse_date':parse_date
                            })    

    return job_result    
         
scrape_jobs()