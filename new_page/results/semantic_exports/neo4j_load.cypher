// Neo4j bulk import option:
// neo4j-admin database import full --nodes=neo4j_nodes.csv --relationships=neo4j_relationships.csv neo4j

// Browser / cypher-shell option after copying CSVs into Neo4j import directory:
LOAD CSV WITH HEADERS FROM 'file:///neo4j_nodes.csv' AS row
MERGE (n:SemanticNode {id: row.`:ID`})
SET n.name = row.name,
    n.source_labels = row.`:LABEL`,
    n.text = row.text,
    n.timestamp = row.timestamp,
    n.target = row.target,
    n.mapped_to_ontology = row.mapped_to_ontology,
    n.records = row.records;

LOAD CSV WITH HEADERS FROM 'file:///neo4j_relationships.csv' AS row
MATCH (a:SemanticNode {id: row.`:START_ID`})
MATCH (b:SemanticNode {id: row.`:END_ID`})
CALL apoc.create.relationship(a, row.`:TYPE`, {}, b) YIELD rel
RETURN count(rel);
