import csv_parsing
from py2neo import neo4j, node, rel


def run():
    # Use csv parsing module to get list of persons with details
    person_list = csv_parsing.run("details.csv")

    # create Neo4j db
    graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
    personen = graph_db.get_or_create_index(neo4j.Node, "Personen")
    print("Created Neo4j db")

    # add persons
    n = 0
    for person in person_list:
        properties = person.details
        full_name = person.firstname + " " + person.surname
        properties["name"] = full_name
        p_node = graph_db.get_or_create_indexed_node("Personen", "name", full_name, properties)
        n += 1
        if n % 20 == 0:
            print("Added " + n + " person nodes to db")

if __name__ == '__main__':
    run()