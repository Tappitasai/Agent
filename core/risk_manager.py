def assess_risk(target_environment, threats):
    """Assess the risk level based on environment and threats."""
    risk_levels = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}

    classification = classify_environment(target_environment)
    risk_score = 0

    for threat in threats:
        risk_score += risk_levels.get(threat.upper(), 0)

    final_risk = "LOW"
    if risk_score >= 7:
        final_risk = "CRITICAL"
    elif risk_score >= 5:
        final_risk = "HIGH"
    elif risk_score >= 3:
        final_risk = "MEDIUM"

    return final_risk, classification


def classify_environment(environment):
    """Classify the target environment to understand context."""
    classifications = {
        "production": "Production Environment",
        "development": "Development Environment",
        "testing": "Testing Environment"
    }

    return classifications.get(environment.lower(), "Unknown Environment")


def automatic_decision_making(risk_level):
    """Make decisions based on risk levels."""
    actions = {
        "LOW": "Monitor the environment.",
        "MEDIUM": "Implement additional controls.",
        "HIGH": "Initiate incident response plan.",
        "CRITICAL": "Engage full incident response team immediately.",
    }

    return actions.get(risk_level, "No action required.")


# Example usage
if __name__ == '__main__':
    environment = "production"
    current_threats = ["HIGH", "MEDIUM"]

    risk_level, env_class = assess_risk(environment, current_threats)
    action = automatic_decision_making(risk_level)
    print(f"Risk Level: {risk_level}, Environment: {env_class}")
    print(f"Recommended Action: {action}")