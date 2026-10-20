
"""
FloodGuard Risk Engine
Educational prototype only.

The thresholds below are illustrative, not official flood-warning
thresholds. Real deployment requires locally validated data.
"""


def assess_risk(rainfall_mm, river_level_m, recent_rainfall_mm=0):
    """
    Estimate an illustrative risk category using:
    - Rainfall over the last 24 hours (mm)
    - River level (m)
    - Recent additional rainfall (mm)

    Returns a dictionary containing the risk category, score,
    color, explanation, advice, and contributing factors.
    """

    # Validate inputs
    values = [rainfall_mm, river_level_m, recent_rainfall_mm]

    if any(value is None for value in values):
        raise ValueError("All risk inputs must have values.")

    if any(value < 0 for value in values):
        raise ValueError("Risk inputs cannot be negative.")

    # These are demo thresholds, NOT official warning limits.
    factors = []

    if rainfall_mm >= 100:
        factors.append("Very heavy 24-hour rainfall")
    elif rainfall_mm >= 50:
        factors.append("Heavy 24-hour rainfall")
    elif rainfall_mm >= 25:
        factors.append("Moderate 24-hour rainfall")

    if recent_rainfall_mm >= 50:
        factors.append("High additional recent rainfall")
    elif recent_rainfall_mm >= 25:
        factors.append("Additional recent rainfall")

    if river_level_m >= 7:
        factors.append("High demo river-level threshold reached")
    elif river_level_m >= 4:
        factors.append("Elevated demo river level")

    # Simple, transparent point system for demonstration.
    score = 0

    if rainfall_mm >= 100:
        score += 2
    elif rainfall_mm >= 50:
        score += 1

    if recent_rainfall_mm >= 50:
        score += 2
    elif recent_rainfall_mm >= 25:
        score += 1

    if river_level_m >= 7:
        score += 2
    elif river_level_m >= 4:
        score += 1

    if score >= 4:
        level = "HIGH"
        color = "#DC2626"
        advice = (
            "Check official weather and disaster-management alerts. "
            "Follow evacuation instructions from local authorities."
        )

    elif score >= 2:
        level = "MODERATE"
        color = "#D97706"
        advice = (
            "Monitor official weather updates and local conditions. "
            "Keep essential supplies and emergency contacts ready."
        )

    else:
        level = "LOW"
        color = "#059669"
        advice = (
            "Continue monitoring local conditions and keep "
            "emergency contacts accessible."
        )

    if not factors:
        factors.append("No demo threshold was reached")

    return {
        "level": level,
        "score": score,
        "max_score": 6,
        "color": color,
        "advice": advice,
        "factors": factors,
        "is_demo": True,
        "disclaimer": (
            "Experimental estimate only. These rules are not validated "
            "for real-world flood prediction or official warnings."
        ),
    }
