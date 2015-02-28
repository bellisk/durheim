# -*- coding: utf-8 -*-

import csv
import sys
import re
import string

RELATIONSHIPS = [
    "Tochter",
    "Sohn",
    "Beihälterin",
    "Beihälter",
    "Ehefrau",
    "Ehemann",
    "Vater",
    "Mutter",
    "Schwester",
    "Bruder"
]

class Person:
    details = {}

    def __init__(self):
        self.surname = ""
        self.firstname = ""
        self.details = {}
        # self.place = ""
        # self.relatives = []
        # self.nickname = ""
        # self.aliases = []
        # self.age = ""


def run(input_filename):
    with open(input_filename) as f:
        persons = []
        reader = csv.DictReader(f)
        for row in reader:
            try:
                caption = row["Original caption"]
                person = Person()

                # What are the fieldnames?
                fields = []
                if re.search("([\w]*):", caption):
                    fields.append(re.search("([\w]*):", caption).group(1))

                # Separate fields for easier parsing
                for fieldname in ["Ort", "Beruf"]:
                    if fieldname in caption and "\n" + fieldname not in caption:
                        caption = string.replace(caption, fieldname, "\n" + fieldname)

                names = re.search("\n?(.*?)\n", caption).group(1)

                if re.search("\nPersonalien: (.*?)\n", caption):
                    personalien = re.search("\nPersonalien: (.*?)\n", caption).group(1)

                if re.search("\nOrt: (.*?)\n", caption):
                    person.details["place"] = re.search("\nOrt: (.*?)\n", caption).group(1)

                if re.search("\nBeruf: (.*?)\n", caption):
                    person.details["job"] = re.search("\nBeruf: (.*?)\n", caption).group(1)

                # Parse out different names
                for w in ["vulgo", "genannt"]:
                    if w in names:
                        person.details["nickname"] = names.split(", " + w + " ")[1]
                        names = names.split(", " + w + " ")[0]

                if "alias" in names:
                    person.details["aliases"] = names.split(", alias ")[1].split(", ")
                    names = names.split(", alias ")[0]

                person.surname = names.split(", ")[0]
                person.firstname = names.split(", ")[1]

                # What can we get out of the Personalien?
                if re.search("([0-9]{2}) Jahre alt", personalien):
                    person.details["age"] = re.search("([0-9]{2}) Jahre alt", personalien).group(1)

                if re.search("geboren.* ([0-9]{4})", personalien):
                    person.details["age"] = 1853 - int(re.search("geboren.* ([0-9]{4})", personalien).group(1))

                for relationship in RELATIONSHIPS:
                    if relationship in personalien:
                        # print(personalien)
                        break

                persons.append(person)
                # print(str(person.details))

            except AttributeError as e:
                print e.message
                continue

        print set(fields)

if __name__ == '__main__':
    input_filename = sys.argv[1]
    run(input_filename)
