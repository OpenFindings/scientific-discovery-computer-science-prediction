"""CS tractability lexicon (CS analogue of Paper 3 facilities.py).

Astronomy tractability depends on which telescopes were operational at the cutoff. The CS
analogue is which shared benchmarks/datasets/platforms existed at the cutoff, whether the work
ships an artifact, and what resources (hardware, human participants, proofs) it needs.
Release years are first public release; a benchmark counts only if released by the cutoff.
"""

from __future__ import annotations

import re

BENCHMARKS: dict[str, tuple[str, int]] = {
    "mnist": (r"\bMNIST\b", 1998), "cifar": (r"\bCIFAR(-?10|-?100)?\b", 2009),
    "imagenet": (r"\bImageNet\b", 2009), "coco": (r"\b(MS[- ]?)?COCO\b", 2014),
    "pascal_voc": (r"\bPASCAL VOC\b", 2005), "kitti": (r"\bKITTI\b", 2012),
    "cityscapes": (r"\bCityscapes\b", 2016), "shapenet": (r"\bShapeNet\b", 2015),
    "penn_treebank": (r"\bPenn Treebank\b", 1993), "squad": (r"\bSQuAD\b", 2016),
    "glue": (r"\bGLUE\b", 2018), "superglue": (r"\bSuperGLUE\b", 2019),
    "wmt": (r"\bWMT\b", 2006), "ms_marco": (r"\bMS ?MARCO\b", 2016),
    "librispeech": (r"\bLibriSpeech\b", 2015), "ale_atari": (r"\b(Atari|Arcade Learning)\b", 2013),
    "mujoco": (r"\bMuJoCo\b", 2012), "openai_gym": (r"\b(OpenAI )?Gym\b", 2016),
    "tpc": (r"\bTPC-?(H|C|DS|E)\b", 1992), "ycsb": (r"\bYCSB\b", 2010),
    "spec": (r"\bSPEC ?(CPU|int|fp|jbb)\w*\b", 1989), "defects4j": (r"\bDefects4J\b", 2014),
    "humaneval": (r"\bHumanEval\b", 2021), "mbpp": (r"\bMBPP\b", 2021),
    "codexglue": (r"\bCodeXGLUE\b", 2021), "sv_comp": (r"\bSV-?COMP\b", 2012),
    "satcomp": (r"\bSAT (Competition|Race)\b", 2002), "dimacs": (r"\bDIMACS\b", 1993),
    "uci": (r"\bUCI (repository|machine learning)\b", 1987), "movielens": (r"\bMovieLens\b", 1998),
    "dblp": (r"\bDBLP\b", 1993), "snap": (r"\bSNAP\b", 2009), "ns3": (r"\bns-?3\b", 2008),
}
_BENCH = {k: (re.compile(p), y) for k, (p, y) in BENCHMARKS.items()}

_RULES = {
    "tra_code_released": r"\b(github\.com|open[- ]source[sd]?|code (is|are)? ?(publicly )?available|"
                         r"we release|publicly release|source code)\b",
    "tra_introduces_artifact": r"\b(we (introduce|present|propose|release|construct|build) "
                               r"(a |an |the )?(new )?(benchmark|dataset|corpus|suite|testbed|tool))",
    "tra_hardware": r"\b(GPU|FPGA|TPU|ASIC|accelerator|hardware)s?\b",
    "tra_large_compute": r"\b(large[- ]scale|billions?|millions? of|distributed training|"
                         r"thousands of (GPUs|machines|nodes))\b",
    "tra_human_study": r"\b(user study|participants|interview\w*|survey(ed)? of|crowdsourc\w+|"
                       r"controlled experiment with)\b",
    "tra_formal_proof": r"\b(we prove|theorem|lemma|proof|lower bound|upper bound|NP-hard)\b",
    "tra_empirical": r"\b(experiment\w*|empirical\w*|evaluat\w+|benchmark\w*|case study)\b",
    "tra_deployment": r"\b(deployed|in production|industrial|real[- ]world deployment|at scale in)\b",
    "tra_simulation": r"\b(simulat\w+|emulat\w+|synthetic data)\b",
}
_RULES_C = {k: re.compile(p, re.I) for k, p in _RULES.items()}


def benchmarks_named(text: str) -> list[str]:
    return [k for k, (pat, _) in _BENCH.items() if pat.search(text or "")]


def tractability_features(text: str, cutoff_year: int) -> dict:
    named = benchmarks_named(text)
    available = [k for k in named if _BENCH[k][1] <= cutoff_year]
    feats = {
        "tra_n_benchmarks_named": len(named),
        "tra_n_benchmarks_available": len(available),
        "tra_uses_shared_benchmark": int(bool(available)),
    }
    for k, pat in _RULES_C.items():
        feats[k] = int(bool(pat.search(text or "")))
    return feats
