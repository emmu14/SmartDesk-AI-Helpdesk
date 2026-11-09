def predict_priority(impact, urgency):

    priority_scores = {
        'low': 1,
        'medium': 2,
        'high': 3,
        'critical': 4
    }

    impact_score = priority_scores.get(impact.lower(), 1)
    urgency_score = priority_scores.get(urgency.lower(), 1)

    total_score = impact_score + urgency_score

    if total_score >= 7:
        return 'critical'

    elif total_score >= 5:
        return 'high'

    elif total_score >= 3:
        return 'medium'

    return 'low'