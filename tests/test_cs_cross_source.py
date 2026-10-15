"""Cross-source label check tests on synthetic fixtures (test-only data; never reported)."""

import numpy as np
import pandas as pd

from cs_forecast import cross_source as cs


def test_s2_window_counts_only_y_plus_1_to_3_and_tracks_null_years():
    years = [2014, 2015, 2016, 2017, 2018, None, None, 2015]
    assert cs.s2_cites_3y(years, 2014) == (4, 2)


def test_kappa_perfect_chance_and_inverse():
    a = np.array([1, 0, 0, 0, 1, 0, 0, 0, 0, 0])
    assert cs.cohen_kappa(a, a) == 1.0
    assert cs.cohen_kappa(a, 1 - a) < 0
    assert np.isnan(cs.cohen_kappa(np.zeros(5), np.zeros(5)))


def test_top_decile_label_is_within_year():
    df = pd.DataFrame({"year": [2010] * 10 + [2011] * 10,
                       "c": list(range(10)) + list(range(100, 110))})
    lab = cs.top_decile_label(df, "c")
    assert lab.tolist() == [0] * 9 + [1] + [0] * 9 + [1]


def test_g4_bands():
    assert cs.g4_verdict(0.8, 0.65) == "robust"
    assert cs.g4_verdict(0.3, 0.1) == "source_dependent"
    assert cs.g4_verdict(0.55, 0.4) == "inconclusive"


def test_bootstrap_identical_labels_gives_kappa_one():
    rng = np.random.default_rng(0)
    c = rng.integers(0, 50, 200)
    df = pd.DataFrame({"year": np.repeat([2015, 2016], 100), "cell": np.repeat(range(20), 10),
                       "ca": c, "cb": c})
    df["a"] = cs.top_decile_label(df, "ca")
    df["b"] = df["a"]
    b = cs.bootstrap_agreement(df, "a", "b", "ca", "cb", reps=50)
    assert b["kappa_ci95"] == [1.0, 1.0] and b["spearman_ci95"][0] > 0.99
