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

FIELDS = [
    'Ort',
    'Beruf',
    'Kennzeichen',
    'Personalien'
]

class Person:
    details = {}

    def __init__(self):
        self.surname = ""
        self.firstname = ""
        self.details = {}


def run(input_filename):
    with open(input_filename) as f:
        persons = []
        reader = csv.DictReader(f)

        for row in reader:
            try:
                caption = row["Original caption"]
                person = Person()

                # Some of the lines have unnecessary newlines. Get rid of them.
                for m in re.findall("(.+)(\n)([^:]+?\n)", caption):
                    caption = string.replace(caption, m[0] + m[1] + m[2], m[0] + " " + m[2])

                for fieldname in FIELDS:
                    # Separate fields for easier parsing
                    if fieldname in caption and "\n" + fieldname not in caption:
                        caption = string.replace(caption, fieldname, "\n" + fieldname)
                    if re.search("\n" + fieldname + ": (.*?)\n", caption):
                        # We parse the Personalien separately later
                        if fieldname == "Personalien":
                            personalien = re.search("\n" + fieldname + ": (.*?)\n", caption).group(1)
                        else:
                            person.details[fieldname] = re.search("\n" + fieldname + ": (.*?)\n", caption).group(1)

                names = re.match("\n?(.*?)\n", caption).group(1)

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
                        print(personalien)
                        break

                persons.append(person)
                print(person.firstname, person.surname, str(person.details))

            except AttributeError as e:
                print caption
                print e.message
                print
                continue

        return persons


if __name__ == '__main__':
    input_filename = sys.argv[1]
    run(input_filename)
