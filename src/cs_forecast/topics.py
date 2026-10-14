"""Transparent keyword classifier for CS subfields (CS analogue of Paper 3 subfields.py).

Each subfield is a list of (regex, weight) rules applied to title + abstract; title matches
count double. The classifier is deliberately rule-based so it can be audited and frozen.
"""

from __future__ import annotations

import re

SUBFIELDS: dict[str, list[tuple[str, int]]] = {
    "machine_learning": [
        (r"\b(deep|neural) (network|learning)s?\b", 2), (r"\bmachine learning\b", 2),
        (r"\b(reinforcement learning|representation learning|generalization)\b", 2),
        (r"\b(gradient descent|SGD|transformer|attention mechanism|embedding)s?\b", 1),
        (r"\b(classifier|classification|regression|supervised|unsupervised)\b", 1),
    ],
    "computer_vision": [
        (r"\b(image|video|visual|vision|pixel|segmentation|object detection)\b", 2),
        (r"\b(convolutional|CNN|camera|3D reconstruction|point cloud)s?\b", 1),
    ],
    "nlp": [
        (r"\b(natural language|language model|NLP|text|translation|parsing|parser)\b", 2),
        (r"\b(sentence|word|token|corpus|question answering|dialog\w*|semantic parsing)s?\b", 1),
    ],
    "robotics": [
        (r"\b(robot\w*|manipulat\w+|locomotion|grasp\w*|embodied|autonomous (vehicle|driving))\b", 3),
        (r"\b(motion planning|SLAM|navigation|drone|UAV)s?\b", 2),
    ],
    "security_privacy": [
        (r"\b(security|attack\w*|adversar\w+|malware|vulnerabilit\w+|intrusion|threat)\b", 2),
        (r"\b(privacy|private|differential privacy|anonymi\w+|leakage)\b", 2),
        (r"\b(authentication|access control|fuzz\w*|exploit\w*)\b", 1),
    ],
    "cryptography": [
        (r"\b(cryptograph\w+|encryption|cipher\w*|signature scheme|zero[- ]knowledge)\b", 3),
        (r"\b(lattice|homomorphic|post-quantum|key exchange|hash function)s?\b", 1),
    ],
    "databases": [
        (r"\b(database|DBMS|SQL|query (processing|optimi\w+)|transaction|indexing)s?\b", 3),
        (r"\b(data management|key-value|OLAP|OLTP|schema|join)s?\b", 1),
    ],
    "distributed_systems": [
        (r"\b(distributed|cloud|datacenter|data center|cluster|serverless|microservice)s?\b", 2),
        (r"\b(consensus|replication|fault[- ]toleran\w+|scheduling|MapReduce|Spark)\b", 1),
    ],
    "networking": [
        (r"\b(network(ing)?|wireless|5G|routing|TCP|packet|bandwidth|SDN|IoT)\b", 2),
        (r"\b(protocol|latency|congestion|edge computing|spectrum)s?\b", 1),
    ],
    "software_engineering": [
        (r"\b(software|developer|code review|testing|test case|bug|defect|refactor\w*)s?\b", 2),
        (r"\b(repair|maintenance|GitHub|open[- ]source project|API usage|technical debt)\b", 1),
    ],
    "programming_languages": [
        (r"\b(programming language|compiler|type system|semantics|lambda calculus)s?\b", 3),
        (r"\b(program synthesis|static analysis|abstract interpretation|DSL|runtime)\b", 1),
    ],
    "formal_methods": [
        (r"\b(formal (verification|methods|specification)|model checking|theorem prov\w+)\b", 3),
        (r"\b(temporal logic|SMT|SAT solver|proof assistant|Coq|Isabelle|invariant)s?\b", 1),
    ],
    "algorithms_theory": [
        (r"\b(algorithm\w*|complexity|NP-hard|approximation|polynomial[- ]time|lower bound)\b", 2),
        (r"\b(graph|combinatori\w+|parameterized|online algorithm|streaming|sublinear)\b", 1),
    ],
    "hci": [
        (r"\b(user study|user interface|human-computer|interaction design|usability|participants)\b", 3),
        (r"\b(users?|crowd\w*|visualization|accessibility)\b", 1),
    ],
    "architecture_hardware": [
        (r"\b(hardware|processor|CPU|GPU|FPGA|ASIC|accelerator|cache|memory hierarchy)s?\b", 2),
        (r"\b(energy[- ]efficien\w+|power consumption|chip|microarchitecture)\b", 1),
    ],
    "multiagent_systems": [
        (r"\b(multi-?agent|agents?|negotiation|game[- ]theor\w+|mechanism design|auction)s?\b", 2),
        (r"\b(coordination|cooperative|equilibri\w+)\b", 1),
    ],
    "optimization": [
        (r"\b(optimi[sz]ation|convex|linear programming|integer programming|heuristic)s?\b", 2),
        (r"\b(scheduling|metaheuristic|evolutionary|genetic algorithm|solver)s?\b", 1),
    ],
}

_COMPILED = {k: [(re.compile(p, re.I), w) for p, w in rules] for k, rules in SUBFIELDS.items()}


def classify(title: str, abstract: str = "") -> dict[str, int]:
    """Return subfield -> score; title matches count double."""
    scores = {}
    for key, rules in _COMPILED.items():
        s = 0
        for pat, w in rules:
            s += 2 * w * len(pat.findall(title or "")) + w * len(pat.findall(abstract or ""))
        scores[key] = s
    return scores


def primary_subfield(title: str, abstract: str = "") -> str:
    scores = classify(title, abstract)
    best = max(scores, key=lambda k: (scores[k], k))
    return best if scores[best] > 0 else "other"
