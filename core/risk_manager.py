# Risk Manager

class RiskManager:
    def __init__(self):
        self.risks = []

    def assess_risk(self, situation):
        # Implement risk assessment logic based on the situation
        risk_level = "Low"
        # Logic to determine risk level
        self.risks.append((situation, risk_level))
        return risk_level

    def make_decision(self, risk_level):
        # Determine decision based on risk level
        if risk_level == "High":
            return "Take caution."
        elif risk_level == "Medium":
            return "Proceed with monitoring."
        else:
            return "Proceed normally."

# Example Usage
if __name__ == "__main__":
    manager = RiskManager()
    risk = manager.assess_risk("Flood forecasted")
    decision = manager.make_decision(risk)
    print(decision)