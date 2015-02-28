# -*- coding: utf-8 -*-

import csv_parsing
from py2neo import neo4j, rel


def run(input_filename):
    # Use csv parsing module to get list of persons with details
    person_list = csv_parsing.run(input_filename)

    # create Neo4j db
    graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
    personen = graph_db.get_or_create_index(neo4j.Node, "Personen")
    personen = graph_db.get_or_create_index(neo4j.Node, "Places")
    print("Created Neo4j db")

    # add persons
    names = []
    n = 0
    for person in person_list:
        properties = {}
        names.append(person.details["name"])

        for key in person.details:
            if key != "relationships":
                properties[key] = person.details[key]

        p1 = graph_db.get_or_create_indexed_node("Personen", "name", person.details["name"], properties)
        p1.add_labels("person")
        n += 1
        if n % 20 == 0:
            print("Added " + str(n) + " person nodes to db")

    for person in person_list:
        # add relationships
        if person.details["relationships"]:
            print(person.details["name"])
            print(person.details["relationships"])
            for relationship in person.details["relationships"]:
                for name in names:
                    # Only create a relationship if we have the related person in the db
                    if name.decode("utf-8") in person.details["relationships"][relationship]:
                        if relationship in ["Sohn", "Tochter"]:
                            # create child relationship
                            child = graph_db.get_or_create_indexed_node("Personen", "name", person.details["name"])
                            parent = graph_db.get_or_create_indexed_node("Personen", "name", name)
                            graph_db.create(rel(child, "Child of", parent))
                            print("Created child-parent relationship for " + person.details["name"] + " and " + name)
                        elif relationship in ["Vater", "Mutter"]:
                            # create parent relationship
                            child = graph_db.get_or_create_indexed_node("Personen", "name", name)
                            parent = graph_db.get_or_create_indexed_node("Personen", "name", person.details["name"])
                            graph_db.create(rel(child, "Child of", parent))
                            print("Created parent-child relationship for " + person.details["name"] + " and " + name)
                        elif relationship in ["Beihälter", "Beihälterin", "Ehefrau", "Ehemann"]:
                            # create partner relationship
                            p1 = graph_db.get_or_create_indexed_node("Personen", "name", name)
                            p2 = graph_db.get_or_create_indexed_node("Personen", "name", person.details["name"])
                            graph_db.create(rel(p1, "Partner to", p2))
                            print("Created partner relationship for " + person.details["name"] + " and " + name)
                        elif relationship in ["Schwester", "Bruder"]:
                            # create sibling relationship
                            s1 = graph_db.get_or_create_indexed_node("Personen", "name", name)
                            s2 = graph_db.get_or_create_indexed_node("Personen", "name", person.details["name"])
                            graph_db.create(rel(s1, "Sibling to", s2))
                            print("Created sibling relationship for " + person.details["name"] + " and " + name)

        # add places
        if "Ort" in person.details:
            p1 = graph_db.get_or_create_indexed_node("Personen", "name", person.details["name"])
            place = graph_db.get_or_create_indexed_node("Places", "place", person.details["Ort"], {"placename": person.details["Ort"]})
            place.add_labels("place")
            graph_db.create(rel(p1, "Comes from", place))
            print("Created 'comes from' relationship for " + person.details["name"] + " and " + person.details["Ort"])



if __name__ == '__main__':
    run()