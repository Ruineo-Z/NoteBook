import pandas as pd
import pytest

from scripts.tcm_hierarchical_clustering import (
    build_cluster_profiles,
    filter_low_frequency_features,
    run_analysis,
    select_best_k,
    sort_cluster_profiles,
    write_analysis_outputs,
)


def test_filter_low_frequency_features_removes_features_below_threshold():
    data = pd.DataFrame(
        {
            "高频症状": [1, 1, 0, 1],
            "边界症状": [1, 0, 0, 0],
            "低频症状": [1, 0, 0, 0],
        }
    )

    filtered, stats = filter_low_frequency_features(
        data,
        min_frequency=0.26,
    )

    assert list(filtered.columns) == ["高频症状"]
    assert stats.loc["边界症状", "keep"] is False
    assert stats.loc["低频症状", "global_frequency"] == pytest.approx(0.25)


def test_filter_low_frequency_features_keeps_features_at_exact_threshold():
    data = pd.DataFrame(
        {
            "刚好阈值": [1] + [0] * 19,
            "高于阈值": [1, 1] + [0] * 18,
        }
    )

    filtered, stats = filter_low_frequency_features(
        data,
        min_frequency=0.05,
    )

    assert "刚好阈值" in filtered.columns
    assert stats.loc["刚好阈值", "keep"] is True


def test_select_best_k_prefers_higher_silhouette_then_ch_index():
    metrics = pd.DataFrame(
        [
            {"k": 4, "silhouette_score": 0.51, "calinski_harabasz_score": 20.0},
            {"k": 5, "silhouette_score": 0.51, "calinski_harabasz_score": 22.0},
            {"k": 6, "silhouette_score": 0.49, "calinski_harabasz_score": 100.0},
        ]
    )

    best = select_best_k(metrics)

    assert best["k"] == 5


def test_build_cluster_profiles_calculates_frequency_and_lift():
    features = pd.DataFrame(
        {
            "乏力": [1, 1, 0, 0],
            "咳嗽": [1, 0, 1, 0],
        }
    )
    labels = pd.Series([1, 1, 2, 2], name="cluster")

    profiles = build_cluster_profiles(features, labels)

    cluster_1_fatigue = profiles[
        (profiles["cluster"] == 1) & (profiles["feature"] == "乏力")
    ].iloc[0]

    assert cluster_1_fatigue["count"] == 2
    assert cluster_1_fatigue["cluster_frequency"] == pytest.approx(1.0)
    assert cluster_1_fatigue["global_frequency"] == pytest.approx(0.5)
    assert cluster_1_fatigue["lift"] == pytest.approx(2.0)


def test_sort_cluster_profiles_prioritizes_frequency_before_lift():
    profiles = pd.DataFrame(
        [
            {
                "cluster": 1,
                "feature": "高频但权重一般",
                "count": 10,
                "cluster_size": 10,
                "cluster_frequency": 1.0,
                "global_frequency": 0.95,
                "lift": 1.05,
            },
            {
                "cluster": 1,
                "feature": "低频但权重高",
                "count": 4,
                "cluster_size": 10,
                "cluster_frequency": 0.4,
                "global_frequency": 0.1,
                "lift": 4.0,
            },
        ]
    )

    sorted_profiles = sort_cluster_profiles(profiles)

    assert list(sorted_profiles["feature"]) == ["高频但权重一般", "低频但权重高"]


def test_run_analysis_and_write_outputs_end_to_end(tmp_path):
    df = pd.DataFrame(
        {
            "姓名": [f"患者{i}" for i in range(1, 13)],
            "年龄": [40 + i for i in range(12)],
            "畏冷": [1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0],
            "咳嗽": [1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0],
            "痰黄": [0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1],
            "口苦": [0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1],
            "乏力": [1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0],
        }
    )
    input_path = tmp_path / "input.xlsx"
    df.to_excel(input_path, index=False)

    result = run_analysis(
        input_path,
        output_dir=tmp_path / "outputs",
        candidate_ks=range(4, 6),
    )

    assert set(result["patient_clusters"]["cluster"]) <= {1, 2, 3, 4, 5}
    assert list(result["k_metrics"]["k"]) == [4, 5]

    output_paths = write_analysis_outputs(result)

    assert output_paths["excel"].exists()
    assert output_paths["dendrogram"].exists()


def test_run_analysis_drops_summary_rows_and_coerces_positive_values(tmp_path):
    df = pd.DataFrame(
        {
            "姓名": [f"患者{i}" for i in range(1, 9)] + [None],
            "年龄": [50 + i for i in range(8)] + [None],
            "畏冷": [1, 1, 0, 0, 1, 1, 0, 0, None],
            "咳嗽": [1, 1, 0, 0, 0, 0, 1, 1, None],
            "泡沫痰多": [3, 1, 0, 0, 0, 0, 1, 1, None],
            "口苦": [0, 0, 1, 1, 0, 0, 1, 1, 10],
        }
    )
    input_path = tmp_path / "dirty_input.xlsx"
    df.to_excel(input_path, index=False)

    result = run_analysis(
        input_path,
        output_dir=tmp_path / "dirty_outputs",
        candidate_ks=range(4, 6),
    )

    sample_count = result["summary"].set_index("metric").loc["sample_count", "value"]
    positive_coercions = result["summary"].set_index("metric").loc["positive_value_coercions", "value"]

    assert sample_count == 8
    assert positive_coercions == 1
