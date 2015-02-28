# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import shutil, csv
import csv_parsing
import durheim_neo4j

BASE_URL = "https://commons.wikimedia.org"
CATEGORY_URLS = [
    "https://commons.wikimedia.org/w/index.php?title=Category:Durheim_portraits_contributed_by_CH-BAR",
    "https://commons.wikimedia.org/w/index.php?title=Category:Durheim_portraits_contributed_by_CH-BAR&filefrom=Sophie+Celestine+Schmied+-+CH-BAR+-+30313983.tif#mw-category-media"
]

def run():
    # get list of urls from the two wikimedia pages
    links = []
    n = 0
    for url in CATEGORY_URLS:
        r = requests.get(url)
        soup = BeautifulSoup(r.text)

        for div in soup.find_all("div", "gallerytext"):
            links.append(div.a.get("href"))
            n += 1
            if n % 20 == 0:
                print "Got " + str(n) + " links to photo pages"

    # download photos and get details of persons
    persons = []
    for link in links:
        r = requests.get(BASE_URL + link)
        soup = BeautifulSoup(r.text)

        for a in soup.find_all("a"):
            if "class" in a.attrs and a["class"][0] == "mw-thumbnail-link":
                # We're getting the preview image shown on the file page as that's an all-right size for now.
                filename = a.get("href").split("/")[-1]
                url = "http:" + a.get("href")
                response = requests.get(url, stream=True)
                print filename
                with open(filename, "w") as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                del response
                print "Downloaded photo " + filename
                break

        # Details to harvest: person depicted, original caption, link on Swiss Archives
        # Other details are the same for all photos
        details = {}
        for tr in soup.table.contents:
            if len(tr) > 1:
                tds = tr.find_all("td")
            else:
                continue
            if tds[0].text in ["Depicted people", "Original caption"]:
                details[tds[0].text] = tds[1].text.encode("utf-8")
            elif tds[0].text == "Accession number":
                details[tds[0].text] = tds[1].a.get("href")

        print details
        persons.append(details)

    # Write details of photos into CSV for easier reference
    headers = ["Depicted people", "Original caption", "Accession number"]
    with open("details.csv", "w") as f:
        writer = csv.DictWriter(f, headers)
        writer.writeheader()
        for person in persons:
            writer.writerow(person)
        print("Wrote row for " + person["Depicted people"])

    # Use csv parsing module to get list of persons with details
    person_list = csv_parsing.run("details.csv")
    print(person_list)

    # Create Neo4j db, add persons and relationships to db
    durheim_neo4j.run("details.csv")

    # Get data on jobs and nicknames into own CSVs
    headers2 = ["Name", "Jobs", "Nicknames"]
    with open("jobs_and_nicknames.csv", "w") as g:
        writer = csv.DictWriter(g, headers2)
        writer.writeheader()
        for person in person_list:
            row = {
                "Name": person.details["name"],
                "Jobs": "",
                "Nicknames": ""
            }

            if "Beruf" in person.details:
                row["Jobs"] = person.details["Beruf"]

            if "nickname" in person.details:
                row["Nicknames"] = str(person.details["nickname"])

            if "Beruf" in person.details or "nickname" in person.details:
                writer.writerow(row)


if __name__ == '__main__':
    run()
