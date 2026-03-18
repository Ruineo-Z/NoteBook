from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import matplotlib
matplotlib.use("Agg")
import pandas as pd
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram, fcluster, linkage
from sklearn.metrics import calinski_harabasz_score, silhouette_score


def normalize_binary_series(series: pd.Series) -> pd.Series:
    normalized = series.fillna(0)
    mapped = normalized.replace(
        {
            True: 1,
            False: 0,
            "1": 1,
            "0": 0,
            "是": 1,
            "否": 0,
            "有": 1,
            "无": 0,
            "阳性": 1,
            "阴性": 0,
        }
    )
    numeric = pd.to_numeric(mapped, errors="coerce")
    if numeric.isna().any():
        bad_values = sorted({value for value in normalized[numeric.isna()].tolist()})
        raise ValueError(f"列 {series.name} 包含无法识别的取值: {bad_values}")
    if (numeric < 0).any():
        bad_values = sorted({value for value in numeric[numeric < 0].tolist()})
        raise ValueError(f"列 {series.name} 包含负数取值: {bad_values}")
    positive_mask = numeric > 0
    coerced = positive_mask.astype(int)
    unique_values = set(coerced.tolist())
    if not unique_values.issubset({0, 1}):
        raise ValueError(f"列 {series.name} 包含非二值取值: {sorted(unique_values)}")
    return coerced


def filter_low_frequency_features(
    features: pd.DataFrame,
    min_frequency: float = 0.05,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    normalized = features.apply(normalize_binary_series)
    global_frequency = normalized.mean(axis=0)
    keep_mask = global_frequency >= min_frequency

    stats = pd.DataFrame(
        {
            "global_frequency": global_frequency,
            "keep": [bool(value) for value in keep_mask.tolist()],
        },
        index=normalized.columns,
    )
    stats["keep"] = stats["keep"].astype(object)
    filtered = normalized.loc[:, keep_mask]
    return filtered, stats


def select_best_k(metrics: pd.DataFrame) -> pd.Series:
    required = {"k", "silhouette_score", "calinski_harabasz_score"}
    missing = required - set(metrics.columns)
    if missing:
        raise ValueError(f"缺少指标列: {sorted(missing)}")
    ranked = metrics.sort_values(
        by=["silhouette_score", "calinski_harabasz_score", "k"],
        ascending=[False, False, True],
    )
    return ranked.iloc[0]


def build_cluster_profiles(
    features: pd.DataFrame,
    labels: pd.Series,
) -> pd.DataFrame:
    normalized = features.apply(normalize_binary_series)
    label_series = pd.Series(labels, index=normalized.index, name="cluster")
    global_frequency = normalized.mean(axis=0)
    rows: list[dict[str, float | int | str]] = []

    for cluster in sorted(label_series.unique()):
        cluster_mask = label_series == cluster
        cluster_frame = normalized.loc[cluster_mask]
        cluster_size = int(cluster_mask.sum())
        cluster_count = cluster_frame.sum(axis=0)
        cluster_frequency = cluster_frame.mean(axis=0)

        for feature in normalized.columns:
            overall = float(global_frequency[feature])
            inside = float(cluster_frequency[feature]) if cluster_size else 0.0
            lift = inside / overall if overall else 0.0
            rows.append(
                {
                    "cluster": int(cluster),
                    "cluster_size": cluster_size,
                    "feature": feature,
                    "count": int(cluster_count[feature]),
                    "cluster_frequency": inside,
                    "global_frequency": overall,
                    "lift": lift,
                }
            )

    return pd.DataFrame(rows)


def sort_cluster_profiles(profiles: pd.DataFrame) -> pd.DataFrame:
    return profiles.sort_values(
        by=["cluster", "cluster_frequency", "lift", "count", "feature"],
        ascending=[True, False, False, False, True],
    ).reset_index(drop=True)


def prepare_feature_matrix(
    data: pd.DataFrame,
    excluded_columns: Iterable[str] = ("姓名", "年龄"),
    min_frequency: float = 0.05,
) -> dict[str, Any]:
    excluded_columns = list(excluded_columns)
    identifier_columns = [col for col in excluded_columns if col in data.columns]
    if identifier_columns:
        summary_row_mask = data[identifier_columns].isna().all(axis=1)
        cleaned_data = data.loc[~summary_row_mask].copy()
    else:
        summary_row_mask = pd.Series(False, index=data.index)
        cleaned_data = data.copy()

    feature_columns = [col for col in data.columns if col not in excluded_columns]
    if not feature_columns:
        raise ValueError("没有可用于聚类的证候列。")

    feature_frame = cleaned_data.loc[:, feature_columns]
    missing_fill_count = int(feature_frame.isna().sum().sum())
    positive_value_coercions = int(
        pd.to_numeric(feature_frame.stack(), errors="coerce").fillna(0).gt(1).sum()
    )
    filtered_features, filter_stats = filter_low_frequency_features(
        feature_frame,
        min_frequency=min_frequency,
    )
    if filtered_features.shape[1] == 0:
        raise ValueError("低频剔除后没有剩余证候列，无法继续聚类。")

    return {
        "cleaned_data": cleaned_data,
        "feature_frame": filtered_features,
        "feature_filter": filter_stats,
        "missing_fill_count": missing_fill_count,
        "dropped_summary_row_count": int(summary_row_mask.sum()),
        "positive_value_coercions": positive_value_coercions,
        "excluded_columns": excluded_columns,
    }


def evaluate_candidate_ks(
    features: pd.DataFrame,
    linkage_matrix,
    candidate_ks: Iterable[int],
) -> pd.DataFrame:
    metrics_rows: list[dict[str, float | int]] = []
    sample_count = len(features)
    for k in candidate_ks:
        if k < 2 or k >= sample_count:
            continue
        labels = pd.Series(fcluster(linkage_matrix, t=k, criterion="maxclust"), index=features.index)
        label_count = labels.nunique()
        if label_count < 2 or label_count >= sample_count:
            continue
        metrics_rows.append(
            {
                "k": int(k),
                "silhouette_score": float(silhouette_score(features, labels, metric="euclidean")),
                "calinski_harabasz_score": float(calinski_harabasz_score(features, labels)),
            }
        )

    if not metrics_rows:
        raise ValueError("候选 K 未生成有效聚类结果，请检查样本量或 K 范围。")
    return pd.DataFrame(metrics_rows)


def create_output_directory(base_output_dir: Path | str | None = None) -> Path:
    root = Path(base_output_dir or "outputs/tcm_clustering")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = root / timestamp
    output_dir.mkdir(parents=True, exist_ok=False)
    return output_dir


def run_analysis(
    input_path: Path | str,
    output_dir: Path | str | None = None,
    excluded_columns: Iterable[str] = ("姓名", "年龄"),
    min_frequency: float = 0.05,
    candidate_ks: Iterable[int] = range(4, 8),
) -> dict[str, Any]:
    input_path = Path(input_path)
    data = pd.read_excel(input_path)
    prepared = prepare_feature_matrix(
        data,
        excluded_columns=excluded_columns,
        min_frequency=min_frequency,
    )
    cleaned_data = prepared["cleaned_data"]
    features = prepared["feature_frame"]
    linkage_matrix = linkage(features, method="ward", metric="euclidean")
    k_metrics = evaluate_candidate_ks(features, linkage_matrix, candidate_ks)
    best_k = select_best_k(k_metrics)
    best_labels = pd.Series(
        fcluster(linkage_matrix, t=int(best_k["k"]), criterion="maxclust"),
        index=features.index,
        name="cluster",
    )

    patient_clusters = cleaned_data.loc[
        :,
        [col for col in cleaned_data.columns if col in excluded_columns],
    ].copy()
    patient_clusters["row_id"] = range(1, len(cleaned_data) + 1)
    patient_clusters["cluster"] = best_labels.values

    cluster_profiles = build_cluster_profiles(features, best_labels)
    cluster_sizes = (
        patient_clusters["cluster"]
        .value_counts()
        .sort_index()
        .rename_axis("cluster")
        .reset_index(name="patient_count")
    )
    summary = pd.DataFrame(
        [
            {"metric": "input_file", "value": str(input_path)},
            {"metric": "sheet_name", "value": "第一个工作表"},
            {"metric": "sample_count", "value": int(len(cleaned_data))},
            {"metric": "raw_row_count", "value": int(len(data))},
            {"metric": "excluded_columns", "value": ",".join(prepared["excluded_columns"])},
            {"metric": "candidate_feature_count", "value": int(len(prepared["feature_filter"]))},
            {"metric": "retained_feature_count", "value": int(features.shape[1])},
            {
                "metric": "removed_feature_count",
                "value": int((~prepared["feature_filter"]["keep"].astype(bool)).sum()),
            },
            {"metric": "missing_fill_count", "value": prepared["missing_fill_count"]},
            {
                "metric": "dropped_summary_row_count",
                "value": prepared["dropped_summary_row_count"],
            },
            {
                "metric": "positive_value_coercions",
                "value": prepared["positive_value_coercions"],
            },
            {"metric": "min_frequency", "value": float(min_frequency)},
            {"metric": "linkage_method", "value": "ward"},
            {"metric": "distance_metric", "value": "euclidean"},
            {"metric": "optimal_k", "value": int(best_k["k"])},
            {"metric": "best_silhouette_score", "value": float(best_k["silhouette_score"])},
            {
                "metric": "best_calinski_harabasz_score",
                "value": float(best_k["calinski_harabasz_score"]),
            },
        ]
    )

    resolved_output_dir = create_output_directory(output_dir)
    return {
        "input_path": input_path,
        "output_dir": resolved_output_dir,
        "raw_data": data,
        "cleaned_data": cleaned_data,
        "features": features,
        "feature_filter": prepared["feature_filter"].reset_index(names="feature"),
        "k_metrics": k_metrics,
        "best_k": best_k,
        "patient_clusters": patient_clusters,
        "cluster_sizes": cluster_sizes,
        "cluster_profiles": sort_cluster_profiles(cluster_profiles),
        "summary": summary,
        "linkage_matrix": linkage_matrix,
    }


def write_analysis_outputs(result: dict[str, Any]) -> dict[str, Path]:
    output_dir = Path(result["output_dir"])
    excel_path = output_dir / "cluster_summary.xlsx"
    dendrogram_path = output_dir / "dendrogram.png"

    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        result["summary"].to_excel(writer, sheet_name="summary", index=False)
        result["k_metrics"].to_excel(writer, sheet_name="k_metrics", index=False)
        result["feature_filter"].to_excel(writer, sheet_name="feature_filter", index=False)
        result["patient_clusters"].to_excel(writer, sheet_name="patient_clusters", index=False)
        result["cluster_sizes"].to_excel(writer, sheet_name="cluster_sizes", index=False)
        result["cluster_profiles"].to_excel(writer, sheet_name="cluster_profiles", index=False)

    plt.rcParams["font.sans-serif"] = [
        "PingFang SC",
        "Hiragino Sans GB",
        "Microsoft YaHei",
        "SimHei",
        "Arial Unicode MS",
        "DejaVu Sans",
    ]
    plt.rcParams["axes.unicode_minus"] = False

    labels = (
        result["patient_clusters"]["姓名"].astype(str).tolist()
        if "姓名" in result["patient_clusters"].columns
        else result["patient_clusters"]["row_id"].astype(str).tolist()
    )
    plt.figure(figsize=(18, 8))
    dendrogram(result["linkage_matrix"], labels=labels, leaf_rotation=90, leaf_font_size=7)
    plt.title("患者层次聚类树状图")
    plt.xlabel("患者")
    plt.ylabel("距离")
    plt.tight_layout()
    plt.savefig(dendrogram_path, dpi=200)
    plt.close()

    return {"excel": excel_path, "dendrogram": dendrogram_path}


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="中医证候层次聚类分析脚本")
    parser.add_argument("--input", required=True, help="输入 Excel 文件路径")
    parser.add_argument(
        "--output-dir",
        default="outputs/tcm_clustering",
        help="输出根目录，脚本会在其下创建时间戳子目录",
    )
    parser.add_argument(
        "--exclude-columns",
        default="姓名,年龄",
        help="要排除的基础信息列，使用英文逗号分隔",
    )
    parser.add_argument(
        "--min-frequency",
        type=float,
        default=0.05,
        help="低频症状剔除阈值，小于该值的症状将被剔除",
    )
    parser.add_argument(
        "--k-range",
        default="4-7",
        help="聚类数探索区间，格式如 4-7",
    )
    return parser


def parse_k_range(raw_range: str) -> range:
    start_text, end_text = raw_range.split("-", maxsplit=1)
    start = int(start_text)
    end = int(end_text)
    if start > end:
        raise ValueError("K 区间起始值不能大于结束值。")
    return range(start, end + 1)


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()
    excluded_columns = [part.strip() for part in args.exclude_columns.split(",") if part.strip()]
    result = run_analysis(
        input_path=args.input,
        output_dir=args.output_dir,
        excluded_columns=excluded_columns,
        min_frequency=args.min_frequency,
        candidate_ks=parse_k_range(args.k_range),
    )
    output_paths = write_analysis_outputs(result)

    print(f"分析完成，最优 K = {int(result['best_k']['k'])}")
    print(f"Excel 输出: {output_paths['excel']}")
    print(f"树状图输出: {output_paths['dendrogram']}")


if __name__ == "__main__":
    main()
