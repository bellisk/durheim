# durheim
Graphing relationships of homeless people photographed by Carl Durheim in Bern, 1852-3.

This code was written for the [1st Swiss Open Cultural Data Hackathon](http://make.opendata.ch/wiki/event:2015-02), 27-28 February 2015.

The idea of this project is to explore this collection of photographs from the Swiss Archives: [Category:Durheim portraits contributed by CH-BAR](https://commons.wikimedia.org/w/index.php?title=Category:Durheim_portraits_contributed_by_CH-BAR). Currently, it is possible to download all of the portraits, parse the associated metadata and load it into a Neo4j graph database. The relationships between people and their places of origin are added to the db and can be browsed with the Neo4j browser interface.

## Usage

- Download and start Neo4j. Open [http://localhost:7474](http://localhost:7474) in a browser.
- In the terminal, enter: python durheim.py
