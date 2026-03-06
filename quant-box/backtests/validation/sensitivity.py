from statistics import mean, pstdev


def parameter_stability(results: list[dict], metric: str = "sharpe") -> dict[str, float]:
    """Quantify sensitivity of a metric over nearby parameter variants.

    Lower dispersion implies higher stability.
    """

    if not results:
        return {"stability_score": 0.0, "metric_mean": 0.0, "metric_std": 0.0}

    values = [float(r.get("metrics", {}).get(metric, 0.0)) for r in results]
    metric_mean = mean(values)
    metric_std = pstdev(values) if len(values) > 1 else 0.0
    coeff_var = abs(metric_std / (metric_mean + 1e-9))
    stability_score = max(0.0, 1.0 - coeff_var)
    return {
        "stability_score": float(stability_score),
        "metric_mean": float(metric_mean),
        "metric_std": float(metric_std),
    }
