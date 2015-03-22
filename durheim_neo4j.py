# -*- coding: utf-8 -*-

import csv_parsing
import json
from py2neo import neo4j, rel


def generate_graph_db(input_filename):
    # Use csv parsing module to get list of persons with details
    person_list = csv_parsing.run(input_filename)

    # create Neo4j db
    graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
    personen = graph_db.get_or_create_index(neo4j.Node, "Personen")
    places = graph_db.get_or_create_index(neo4j.Node, "Places")
    print("Created Neo4j db")

    # add persons
    names = []
    dupe_names = []
    n = 0
    for person in person_list:
        properties = {}
        name = person.details["name"]

        if name in names:
            dupe_names.append(name)

        names.append(name)

        for key in person.details:
            if key != "relationships":
                properties[key] = person.details[key]

        p1 = graph_db.get_or_create_indexed_node("Personen", "name", name, properties)
        p1.add_labels("person")
        n += 1

        if n % 20 == 0:
            print("Added " + str(n) + " person nodes to db")

    print(dupe_names)
    difficult_relationships = []

    # add relationships
    for person in person_list:
        source_name = person.details["name"]

        # There are some annoying cases that need to be done by hand
        if source_name in dupe_names or "Joseph Bergdorf" in source_name:
            difficult_relationships.append(person)
            continue

        add_relationships(person, names)

        # add places
        if "Ort" in person.details:
            p1 = graph_db.get_or_create_indexed_node("Personen", "name", person.details["name"])
            place = graph_db.get_or_create_indexed_node("Places", "place", person.details["Ort"], {"placename": person.details["Ort"]})
            place.add_labels("place")
            properties = {"type": "FROM"}
            graph_db.create(rel(p1, ("FROM", properties), place))
            # print("Created FROM relationship for " + person.details["name"] + " and " + person.details["Ort"])

    print(difficult_relationships)

    for person in difficult_relationships:
        add_relationships(person, names)

def add_relationships(person, names):
    source_name = person.details["name"]
    graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
    if person.details["relationships"]:
        for relationship in person.details["relationships"]:
            for target_name in names:
                # Only create a relationship if we have the related person in the db
                if target_name.decode("utf-8") in person.details["relationships"][relationship]:
                    if target_name == "Joseph Bergdorf":
                        if "Urs Joseph Bergdorf" in person.details["relationships"][relationship]:
                            continue
                    if relationship in ["Sohn", "Tochter"]:
                        r_type = "CHILD"
                    elif relationship in ["Vater", "Mutter"]:
                        r_type = "CHILD"
                        old_source_name = source_name
                        source_name = target_name
                        target_name = old_source_name
                    elif relationship in ["Beihälter", "Beihälterin", "Ehefrau", "Ehemann"]:
                        r_type = "PARTNER"
                    elif relationship in ["Schwester", "Bruder"]:
                        r_type = "SIBLING"

                    s = graph_db.get_or_create_indexed_node("Personen", "name", source_name)
                    t = graph_db.get_or_create_indexed_node("Personen", "name", target_name)
                    properties = {"type": r_type}

                    graph_db.create(rel(s, (r_type, properties), t))
                    # print("Created " + r_type + " relationship for " + source_name + " and " + target_name)

def add_implied_relationships():
    graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
    query = neo4j.CypherQuery(
        graph_db,
        "MATCH (a:person)<-[r1:CHILD]-(b:person)-[r2:CHILD]->(c:person) "
        "WHERE NOT (a)-[]-(c) "
        "RETURN a, c"
    )
    results = query.execute()
    properties = {"type": "PARTNER"}
    partners = {}

    for source, target in results:
        if source["name"] in partners and partners[source["name"]] == target["name"]:
            continue
        elif target["name"] in partners and partners[target["name"]] == source["name"]:
            continue

        graph_db.create(rel(source, ("PARTNER", properties), target))
        partners[source["name"]] = target["name"]
        print("Created implied PARTNER relationship for " + source["name"] + " and " + target["name"])


def get_graph():
    graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")

    # Interpersonal relationships
    query = neo4j.CypherQuery(
        graph_db,
        "MATCH (a:person)-[r]->(b:person) "
        "RETURN a, r, b"
    )
    results = query.execute()
    nodes = []
    rels = []
    i = 0
    names = {}
    for p1, r1, p2 in results:
        for p in (p1, p2):
            if p["name"] not in names:
                nodes.append({"title": p["name"], "label": "person", "id": i})
                names[p["name"]] = i
                i += 1
        rels.append({"source": names[p1["name"]], "target": names[p2["name"]], "type": r1.type})
    print json.dumps({"nodes": nodes, "links": rels})
    print len(nodes)


if __name__ == '__main__':
    generate_graph_db('details.csv')
    # add_implied_relationships()
    # get_graph()
