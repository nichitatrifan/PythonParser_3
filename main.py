import requests
import lxml
import json
import time
import random

from bs4 import BeautifulSoup
from requests.api import head


def main():
    
    proxies = {
        "https": "your_proxy_ip:port"
    }
    
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    }

    festival_links = []
    folder_path = "C:/Users/nichi/Projects/WebParser/lesson4/data"
    final_json = []
    
    # max offset = 192
    # collect all festival links
    for offset in range(0, 192, 24):

        data_source_html_path = folder_path + f"/source_data_{offset}.html"
        

        url = f"https://www.skiddle.com/festivals/search/?ajaxing=1&sort=0&fest_name=&from_date=19%20Dec%202021&to_date=&maxprice=500&o={offset}&bannertitle=April"
        response = requests.get(url=url, headers=headers) # proxies=proxies

        response_json_data = json.loads(response.text)
        html_data = response_json_data["html"]

        with open(data_source_html_path, "w", encoding="utf-8") as file:
            file.write(html_data)

        # Selectors on the browsing page!!
        #
        # .card -> festival's 'div'
        # .card-img -> img url
        # .card-img-link -> festival's url
        # .card-title -> festival's title
        #

        with open(data_source_html_path, 'r', encoding="utf-8") as file:
            source_html = file.read()
        
        soup = BeautifulSoup(source_html, "lxml")

        festivals_links_tags = soup.select(".card-img-link")
        
        
        for path in festivals_links_tags:
            festival_links.append("https://www.skiddle.com/" + path["href"])
            
    # get each festival's page and parse all the info
    for i, festival in enumerate(festival_links):
        
        time.sleep(random.randint(0, 3))
        print("collecting: "+ festival, end=" ")
        print("Number: " + str(i))
        
        response = requests.get(url=festival, headers=headers)
        
        festival_source = folder_path + f"/festival_source_{i}.html"
        data_json_path = folder_path + f"/festival_data_{i}.json"
        
        with open(festival_source, "w", encoding="utf-8") as file:
            file.write(response.text)
            soup = BeautifulSoup(response.text, "lxml")

        # parse information from each festival's page
        #
        # .scroll-img -> img src
        # .top-info-cont>h1 -> festival's name
        # .top-info-cont>h3 -> festival's date
        # .top-info-cont>p>a:first-of-type -> href for the place
        # .top-info-cont>p>span.bold -> minimum age
        #
        no_page = False
        
        try:
            img_src = soup.select_one(".scroll-img")["src"]
        except:
            img_src = "NONE"
            no_page = True
        
        if no_page:
            festival_date = "NONE"
            festival_location_link = "NONE"
            minimum_age = "NONE"
        else:
            festival_name = soup.select_one(".top-info-cont>h1").text
            festival_date = soup.select_one(".top-info-cont>h3").text
            festival_location_link = "https://www.skiddle.com/" + soup.select_one(".top-info-cont>p>a:first-of-type")["href"]
            try:
                minimum_age = soup.select_one(".top-info-cont>p>span.bold").text
            except:
                minimum_age = "0"
            
        festival_dict = {
                "Link": festival,
                "IMG": img_src,
                "Name": festival_name,
                "Date": festival_date,
                "Location_Link": festival_location_link,
                "Minimum_Age": minimum_age
            }

        final_json.append(festival_dict)
    
    with open(data_json_path, 'w', encoding="utf-8") as file:
        json.dump(final_json, file, indent=4, ensure_ascii=False)
        


if __name__ == "__main__":
    main()