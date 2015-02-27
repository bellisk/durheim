from bs4 import BeautifulSoup
import requests
import re, os


BASE_URL = "https://commons.wikimedia.org/wiki/"
CATEGORY_URLS = [
    "Category:Durheim_portraits_contributed_by_CH-BAR",
    "https://commons.wikimedia.org/w/index.php?title=Category:Durheim_portraits_contributed_by_CH-BAR&filefrom=Sophie+Celestine+Schmied+-+CH-BAR+-+30313983.tif#mw-category-media"
]

def run():
    # get list of urls from the two wikimedia pages
    r = requests.get("https://commons.wikimedia.org/w/index.php?title=Category:Durheim_portraits_contributed_by_CH-BAR")
    soup = BeautifulSoup(r.text)
    print soup
    
    # download photos
    # get details of persons
    # get relationships
    # create Neo4j db
    # add persons and relationships to db
