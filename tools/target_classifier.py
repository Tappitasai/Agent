import os

class TargetEnvironmentClassifier:
    def __init__(self, target_url):
        self.target_url = target_url

    def classify_target(self):
        # Logic to classify the target environment
        if 'lab' in self.target_url:
            return 'lab'
        elif 'ctf' in self.target_url:
            return 'CTF'
        elif 'production' in self.target_url:
            return 'production'
        else:
            return 'unknown'

    def restrict_automation(self):
        classification = self.classify_target()
        if classification == 'production':
            print('Automation restricted on production environment')
            return True
        else:
            print('Automation allowed on non-production environment')
            return False

# Example usage
if __name__ == '__main__':
    target_classifier = TargetEnvironmentClassifier('http://example.com/lab')
    print(target_classifier.restrict_automation()) # Adjust target string accordingly
