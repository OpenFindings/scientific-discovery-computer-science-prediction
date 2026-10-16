"""Pipeline tests on a synthetic fixture (test-only data; never reported as results)."""

import numpy as np
import pandas as pd

from cs_forecast import evaluate as ev
from cs_forecast.features import outcome, paper_features, retrieval_features
from cs_forecast.topics import primary_subfield
from cs_forecast.tractability import tractability_features


def test_topic_classifier_routes_obvious_titles():
    assert primary_subfield("A lattice-based encryption scheme") == "cryptography"
    assert primary_subfield("Query optimization in a column-store DBMS") == "databases"
    assert primary_subfield("Grasping with a robot arm") == "robotics"
    assert primary_subfield("zzz") == "other"


def test_benchmark_counts_only_if_released_by_cutoff():
    f = tractability_features("We evaluate on HumanEval and ImageNet.", 2019)
    assert f["tra_n_benchmarks_named"] == 2 and f["tra_n_benchmarks_available"] == 1


def _paper(y, cites, refs):
    return {"paper_id": f"p{y}", "year": y, "published": f"{y}-06-01T00:00:00Z",
            "title": "A new algorithm", "abstract": "We prove a lower bound.",
            "refs": refs, "topics": [], "topic_pairs": [], "cites_by_year": cites,
            "n_authors": 2, "author_prior_works": {"a": 3}}


def test_future_references_and_citations_never_enter_features():
    refs = [{"year": 2012, "topic": "T1"}, {"year": 2016, "topic": "T2"}]
    p = _paper(2014, {"2014": 2, "2015": 5, "2016": 7, "2017": 1, "2018": 100}, refs)
    f = paper_features(p, {}, {})
    assert f["ev_n_refs"] == 1  # the 2016 reference is after the 2014 cutoff
    assert abs(f["base_cites_year0_log"] - np.log1p(2)) < 1e-12
    assert outcome(p) == 13  # 2015-2017 only


def test_author_without_openalex_id_is_missing_not_zero():
    p = _paper(2014, {}, [])
    p["author_prior_works"] = {"a": 3, "null": 0}
    f = paper_features(p, {}, {})
    assert abs(f["base_author_prior_mean_log"] - np.log1p(3)) < 1e-12
    p["author_prior_works"] = {"null": 0}
    assert np.isnan(paper_features(p, {}, {})["base_author_prior_max_log"])


def test_retrieval_uses_only_earlier_years():
    texts = ["graph algorithm"] * 6 + ["graph algorithm", "graph algorithm"]
    years = [2010] * 6 + [2010, 2011]
    out = retrieval_features(texts, years, ["t"] * 8)
    assert np.isnan(out[6]["nov_nn_distance"])  # 2010 has no earlier papers
    assert out[7]["nov_nn_distance"] < 1e-9


def test_rolling_origin_embargo():
    rng = np.random.default_rng(0)
    n = 400
    df = pd.DataFrame({"paper_id": range(n), "year": rng.integers(2010, 2023, n),
                       "txt_x": rng.normal(size=n), "env_topic_growth": rng.normal(size=n)})
    df["cell"] = df.year.astype(str)
    df["cites_3y"] = rng.poisson(5, n)
    df["y"] = (df.txt_x + rng.normal(size=n) > 1.2).astype(int)
    seen = []

    def spy(tr, te, t):
        seen.append((tr.year.max(), te.year.min()))
        return np.full(len(te), 0.5)

    ev.rolling_origin(df, "y", {"spy": spy})
    assert all(trmax <= temin - ev.EMBARGO for trmax, temin in seen)
    m = ev.metrics(df.y, 1 / (1 + np.exp(-df.txt_x)), df.cites_3y)
    assert 0.5 < m["auroc"] <= 1
