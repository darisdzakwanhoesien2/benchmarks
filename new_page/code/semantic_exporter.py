from __future__ import annotations

import csv
import html
import io
import json
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
VIS = RESULTS / "visualizations"
REVISION = RESULTS / "revision_analysis"
EXPORT_DIR = RESULTS / "semantic_exports"

BASE_IRI = "https://esg-thesis.darisdzakwanhoesien.site/ontology/"
RESOURCE_IRI = "https://esg-thesis.darisdzakwanhoesien.site/resource/"


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path).fillna("")
    except Exception:
        return pd.DataFrame()


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def slug(value: object, fallback: str = "unknown") -> str:
    text = str(value or "").strip()
    if not text:
        text = fallback
    text = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()
    return text or fallback


def turtle_literal(value: object) -> str:
    text = str(value or "")
    return json.dumps(text, ensure_ascii=False)


def xml_text(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def split_labels(value: object) -> list[str]:
    text = str(value or "").strip()
    if not text:
        return []
    if text.startswith("[") and text.endswith("]"):
        try:
            parsed = json.loads(text.replace("'", '"'))
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except Exception:
            pass
    return [part.strip() for part in re.split(r"[|,;]", text) if part.strip()]


@dataclass(frozen=True)
class SemanticBundle:
    tone_records: pd.DataFrame
    silver: pd.DataFrame
    ontology_coverage: pd.DataFrame
    ontology_json: dict


def load_semantic_bundle() -> SemanticBundle:
    return SemanticBundle(
        tone_records=load_csv(VIS / "tone_records_flat.csv"),
        silver=load_csv(REVISION / "silver_tone_ground_truth.csv"),
        ontology_coverage=load_csv(REVISION / "ontology_coverage.csv"),
        ontology_json=load_json(REVISION / "ontology.json", {}),
    )


def canonical_records(bundle: SemanticBundle, limit: int | None = None) -> pd.DataFrame:
    df = bundle.silver.copy() if not bundle.silver.empty else bundle.tone_records.copy()
    if df.empty:
        return df
    rename = {"tone": "tone_pred", "target_doc": "company"}
    for old, new in rename.items():
        if old in df.columns and new not in df.columns:
            df[new] = df[old]
    if "record_id" not in df.columns:
        if {"run_idx", "record_idx"}.issubset(df.columns):
            df["record_id"] = df.apply(lambda r: f"r{int(r['run_idx']):03d}_{int(r['record_idx']):03d}", axis=1)
        else:
            df["record_id"] = [f"r{i:06d}" for i in range(len(df))]
    if "company" not in df.columns:
        if "target" in df.columns:
            df["company"] = df["target"].astype(str).str.split("/").str[0].str.replace("_pdf", "", regex=False)
        else:
            df["company"] = "unknown"
    wanted = [
        "record_id",
        "run_idx",
        "record_idx",
        "timestamp",
        "model",
        "prompt",
        "target",
        "company",
        "text",
        "aspect",
        "esg",
        "tone_pred",
        "silver_tone_ground_truth",
        "sentiment",
        "sentiment_score",
        "labels",
        "reasoning",
        "language",
    ]
    cols = [col for col in wanted if col in df.columns]
    out = df[cols].copy()
    if limit is not None:
        out = out.head(limit)
    return out.astype("object").where(pd.notna(out), "")


def ontology_rows(bundle: SemanticBundle) -> pd.DataFrame:
    rows = []
    coverage = bundle.ontology_coverage.copy()
    if not coverage.empty:
        rows.extend(coverage.to_dict("records"))
    seen = {slug(row.get("aspect")) for row in rows}
    for node in bundle.ontology_json.get("nodes", []):
        if not isinstance(node, dict):
            continue
        aspect = node.get("aspect", "")
        key = slug(aspect)
        if key in seen:
            continue
        rows.append(
            {
                "aspect": aspect,
                "records": 0,
                "mapped_to_ontology": True,
                "suggested_path": node.get("path_text") or " -> ".join(node.get("path", [])),
            }
        )
    return pd.DataFrame(rows).fillna("")


def _class_individual_lines(class_name: str, values: Iterable[object]) -> list[str]:
    lines: list[str] = []
    for value in sorted({str(v).strip() for v in values if str(v).strip()}):
        ident = slug(value)
        lines.extend(
            [
                f"esgr:{class_name}_{ident} a esg:{class_name} ;",
                f"    rdfs:label {turtle_literal(value)} .",
                "",
            ]
        )
    return lines


def build_turtle(bundle: SemanticBundle, limit: int | None = None) -> str:
    records = canonical_records(bundle, limit)
    onto = ontology_rows(bundle)
    lines = [
        "@prefix esg: <https://esg-thesis.darisdzakwanhoesien.site/ontology/> .",
        "@prefix esgr: <https://esg-thesis.darisdzakwanhoesien.site/resource/> .",
        "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
        "",
        "esg: a owl:Ontology ;",
        '    rdfs:label "ESG thesis semantic export ontology" .',
        "",
    ]
    for cls in ["ESGRecord", "Company", "Model", "Prompt", "Aspect", "ESGPillar", "Tone", "Sentiment", "OntologyPath", "ClimateLabel"]:
        lines.append(f"esg:{cls} a owl:Class .")
    lines.append("")
    for prop in ["fromCompany", "generatedByModel", "usedPrompt", "hasAspect", "hasPillar", "hasTone", "hasSentiment", "hasClimateLabel", "mappedToPath"]:
        lines.append(f"esg:{prop} a owl:ObjectProperty .")
    for prop in ["recordText", "reasoning", "timestamp", "sentimentScore", "recordIndex", "runIndex", "sourceTarget", "mappedToOntology"]:
        lines.append(f"esg:{prop} a owl:DatatypeProperty .")
    lines.append("")

    if not records.empty:
        lines.extend(_class_individual_lines("Company", records.get("company", [])))
        lines.extend(_class_individual_lines("Model", records.get("model", [])))
        lines.extend(_class_individual_lines("Prompt", records.get("prompt", [])))
        lines.extend(_class_individual_lines("Aspect", records.get("aspect", [])))
        lines.extend(_class_individual_lines("ESGPillar", records.get("esg", [])))
        lines.extend(_class_individual_lines("Tone", records.get("tone_pred", [])))
        lines.extend(_class_individual_lines("Sentiment", records.get("sentiment", [])))
        label_values = []
        for labels in records.get("labels", []):
            label_values.extend(split_labels(labels))
        lines.extend(_class_individual_lines("ClimateLabel", label_values))

    for _, row in onto.iterrows():
        aspect = str(row.get("aspect", "")).strip()
        path = str(row.get("suggested_path", "")).strip()
        if not path:
            continue
        lines.extend(
            [
                f"esgr:OntologyPath_{slug(path)} a esg:OntologyPath ;",
                f"    rdfs:label {turtle_literal(path)} .",
                "",
            ]
        )
        if aspect:
            mapped = "true" if str(row.get("mapped_to_ontology", "")).lower() in {"true", "1", "yes"} else "false"
            lines.extend(
                [
                    f"esgr:Aspect_{slug(aspect)} esg:mappedToPath esgr:OntologyPath_{slug(path)} ;",
                    f"    esg:mappedToOntology {mapped} .",
                    "",
                ]
            )

    for _, row in records.iterrows():
        rid = slug(row.get("record_id"), "record")
        statements = [f"esgr:Record_{rid} a esg:ESGRecord"]
        links = [
            ("fromCompany", "Company", row.get("company")),
            ("generatedByModel", "Model", row.get("model")),
            ("usedPrompt", "Prompt", row.get("prompt")),
            ("hasAspect", "Aspect", row.get("aspect")),
            ("hasPillar", "ESGPillar", row.get("esg")),
            ("hasTone", "Tone", row.get("tone_pred")),
            ("hasSentiment", "Sentiment", row.get("sentiment")),
        ]
        for prop, cls, value in links:
            if str(value or "").strip():
                statements.append(f"    esg:{prop} esgr:{cls}_{slug(value)}")
        for label in split_labels(row.get("labels", "")):
            statements.append(f"    esg:hasClimateLabel esgr:ClimateLabel_{slug(label)}")
        literals = [
            ("recordText", row.get("text")),
            ("reasoning", row.get("reasoning")),
            ("timestamp", row.get("timestamp")),
            ("sourceTarget", row.get("target")),
            ("runIndex", row.get("run_idx")),
            ("recordIndex", row.get("record_idx")),
            ("sentimentScore", row.get("sentiment_score")),
        ]
        for prop, value in literals:
            if str(value or "").strip():
                statements.append(f"    esg:{prop} {turtle_literal(value)}")
        lines.append(" ;\n".join(statements) + " .")
        lines.append("")
    return "\n".join(lines)


def build_owl_xml(bundle: SemanticBundle, limit: int | None = None) -> str:
    records = canonical_records(bundle, limit)
    onto = ontology_rows(bundle)
    chunks = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" xmlns:owl="http://www.w3.org/2002/07/owl#" xmlns:esg="{BASE_IRI}">',
        f'  <owl:Ontology rdf:about="{BASE_IRI}">',
        "    <rdfs:label>ESG thesis semantic export ontology</rdfs:label>",
        "  </owl:Ontology>",
    ]
    for cls in ["ESGRecord", "Company", "Model", "Prompt", "Aspect", "ESGPillar", "Tone", "Sentiment", "OntologyPath", "ClimateLabel"]:
        chunks.append(f'  <owl:Class rdf:about="{BASE_IRI}{cls}"/>')
    for prop in ["fromCompany", "generatedByModel", "usedPrompt", "hasAspect", "hasPillar", "hasTone", "hasSentiment", "hasClimateLabel", "mappedToPath"]:
        chunks.append(f'  <owl:ObjectProperty rdf:about="{BASE_IRI}{prop}"/>')
    for prop in ["recordText", "reasoning", "timestamp", "sentimentScore", "recordIndex", "runIndex", "sourceTarget", "mappedToOntology"]:
        chunks.append(f'  <owl:DatatypeProperty rdf:about="{BASE_IRI}{prop}"/>')

    for _, row in onto.iterrows():
        aspect = str(row.get("aspect", "")).strip()
        path = str(row.get("suggested_path", "")).strip()
        if aspect:
            chunks.append(f'  <owl:NamedIndividual rdf:about="{RESOURCE_IRI}Aspect_{slug(aspect)}"><rdf:type rdf:resource="{BASE_IRI}Aspect"/><rdfs:label>{xml_text(aspect)}</rdfs:label></owl:NamedIndividual>')
        if path:
            chunks.append(f'  <owl:NamedIndividual rdf:about="{RESOURCE_IRI}OntologyPath_{slug(path)}"><rdf:type rdf:resource="{BASE_IRI}OntologyPath"/><rdfs:label>{xml_text(path)}</rdfs:label></owl:NamedIndividual>')

    emitted: set[str] = set()
    for cls, col in [("Company", "company"), ("Model", "model"), ("Prompt", "prompt"), ("Aspect", "aspect"), ("ESGPillar", "esg"), ("Tone", "tone_pred"), ("Sentiment", "sentiment")]:
        if col not in records.columns:
            continue
        for value in sorted({str(v).strip() for v in records[col] if str(v).strip()}):
            key = f"{cls}:{slug(value)}"
            if key in emitted:
                continue
            emitted.add(key)
            chunks.append(f'  <owl:NamedIndividual rdf:about="{RESOURCE_IRI}{cls}_{slug(value)}"><rdf:type rdf:resource="{BASE_IRI}{cls}"/><rdfs:label>{xml_text(value)}</rdfs:label></owl:NamedIndividual>')

    for _, row in records.iterrows():
        rid = slug(row.get("record_id"), "record")
        chunks.append(f'  <owl:NamedIndividual rdf:about="{RESOURCE_IRI}Record_{rid}">')
        chunks.append(f'    <rdf:type rdf:resource="{BASE_IRI}ESGRecord"/>')
        for prop, cls, value in [
            ("fromCompany", "Company", row.get("company")),
            ("generatedByModel", "Model", row.get("model")),
            ("usedPrompt", "Prompt", row.get("prompt")),
            ("hasAspect", "Aspect", row.get("aspect")),
            ("hasPillar", "ESGPillar", row.get("esg")),
            ("hasTone", "Tone", row.get("tone_pred")),
            ("hasSentiment", "Sentiment", row.get("sentiment")),
        ]:
            if str(value or "").strip():
                chunks.append(f'    <esg:{prop} rdf:resource="{RESOURCE_IRI}{cls}_{slug(value)}"/>')
        for prop, value in [("recordText", row.get("text")), ("reasoning", row.get("reasoning")), ("timestamp", row.get("timestamp")), ("sourceTarget", row.get("target"))]:
            if str(value or "").strip():
                chunks.append(f"    <esg:{prop}>{xml_text(value)}</esg:{prop}>")
        chunks.append("  </owl:NamedIndividual>")
    chunks.append("</rdf:RDF>")
    return "\n".join(chunks)


def _csv_bytes(rows: list[dict[str, object]], fieldnames: list[str]) -> bytes:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def build_neo4j_files(bundle: SemanticBundle, limit: int | None = None) -> dict[str, bytes]:
    records = canonical_records(bundle, limit)
    onto = ontology_rows(bundle)
    nodes: dict[str, dict[str, object]] = {}
    rels: list[dict[str, object]] = []

    def add_node(node_id: str, labels: str, name: object = "", **props) -> None:
        nodes[node_id] = {":ID": node_id, ":LABEL": labels, "name": str(name or ""), **props}

    def add_rel(start: str, end: str, rel_type: str, **props) -> None:
        if start and end:
            rels.append({":START_ID": start, ":END_ID": end, ":TYPE": rel_type, **props})

    for _, row in records.iterrows():
        rid = f"record:{slug(row.get('record_id'), 'record')}"
        add_node(rid, "ESGRecord", row.get("record_id"), text=row.get("text", ""), timestamp=row.get("timestamp", ""), target=row.get("target", ""))
        for col, label, rel in [
            ("company", "Company", "FROM_COMPANY"),
            ("model", "Model", "GENERATED_BY_MODEL"),
            ("prompt", "Prompt", "USED_PROMPT"),
            ("aspect", "Aspect", "HAS_ASPECT"),
            ("esg", "ESGPillar", "HAS_PILLAR"),
            ("tone_pred", "Tone", "HAS_TONE"),
            ("sentiment", "Sentiment", "HAS_SENTIMENT"),
        ]:
            value = row.get(col)
            if str(value or "").strip():
                nid = f"{label.lower()}:{slug(value)}"
                add_node(nid, label, value)
                add_rel(rid, nid, rel)
        for label_value in split_labels(row.get("labels", "")):
            nid = f"climatelabel:{slug(label_value)}"
            add_node(nid, "ClimateLabel", label_value)
            add_rel(rid, nid, "HAS_CLIMATE_LABEL")

    for _, row in onto.iterrows():
        aspect = str(row.get("aspect", "")).strip()
        path = str(row.get("suggested_path", "")).strip()
        if not aspect or not path:
            continue
        aspect_id = f"aspect:{slug(aspect)}"
        path_id = f"ontologypath:{slug(path)}"
        add_node(aspect_id, "Aspect", aspect)
        add_node(path_id, "OntologyPath", path, mapped_to_ontology=str(row.get("mapped_to_ontology", "")), records=row.get("records", ""))
        add_rel(aspect_id, path_id, "MAPPED_TO_PATH")

    node_fields = [":ID", ":LABEL", "name", "text", "timestamp", "target", "mapped_to_ontology", "records"]
    rel_fields = [":START_ID", ":END_ID", ":TYPE"]
    cypher = """// Neo4j bulk import option:
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
"""
    return {
        "neo4j_nodes.csv": _csv_bytes(list(nodes.values()), node_fields),
        "neo4j_relationships.csv": _csv_bytes(rels, rel_fields),
        "neo4j_load.cypher": cypher.encode("utf-8"),
    }


def export_all(bundle: SemanticBundle, limit: int | None = None) -> dict[str, bytes]:
    files = {
        "esg_thesis_graph.ttl": build_turtle(bundle, limit).encode("utf-8"),
        "esg_thesis_ontology.owl": build_owl_xml(bundle, limit).encode("utf-8"),
    }
    files.update(build_neo4j_files(bundle, limit))
    return files


def write_exports(bundle: SemanticBundle, limit: int | None = None, out_dir: Path = EXPORT_DIR) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, content in export_all(bundle, limit).items():
        path = out_dir / name
        path.write_bytes(content)
        paths[name] = path
    zip_path = out_dir / "esg_semantic_exports.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, path in paths.items():
            zf.write(path, arcname=name)
    paths[zip_path.name] = zip_path
    return paths


def zip_bytes(files: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return buffer.getvalue()
