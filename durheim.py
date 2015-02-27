from bs4 import BeautifulSoup
import requests
import shutil


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
        
        
        break
    
    # get relationships
    # create Neo4j db
    # add persons and relationships to db
    
if __name__ == '__main__':
    run()
