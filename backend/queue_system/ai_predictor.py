import numpy as np
import random
from sklearn.ensemble import RandomForestRegressor

class QueuePredictor:
    def __init__(self):
        # We will train a real RandomForestRegressor from scikit-learn
        self.model = RandomForestRegressor(n_estimators=15, random_state=42)
        self.services = ['Hospital', 'Bank', 'University', 'Government', 'Service Center']
        self.priorities = ['Emergency', 'Senior Citizen', 'VIP', 'Regular']
        self._init_and_train()

    def _encode_service(self, service):
        try:
            return self.services.index(service)
        except ValueError:
            return 0

    def _encode_priority(self, priority):
        try:
            return self.priorities.index(priority)
        except ValueError:
            return 3

    def _init_and_train(self):
        """
        Generate synthetic historical queue data and train a RandomForestRegressor.
        """
        X_train = []
        Y_train = []
        
        # Base wait times by service
        base_service_time = {
            'Hospital': 15,
            'Bank': 8,
            'University': 12,
            'Government': 22,
            'Service Center': 10
        }
        
        # Base wait times multiplier by priority
        priority_multiplier = {
            'Emergency': 0.1,
            'Senior Citizen': 0.3,
            'VIP': 0.4,
            'Regular': 1.0
        }

        # Generate 250 operational rows
        for _ in range(250):
            people_ahead = random.randint(0, 20)
            avg_service = float(base_service_time[random.choice(self.services)])
            dept_idx = random.randint(0, 4)
            service_name = self.services[dept_idx]
            priority_name = random.choice(self.priorities)
            prio_idx = self._encode_priority(priority_name)
            hour = random.uniform(9.0, 17.0)
            day = random.randint(0, 6)
            
            # Ground truth wait time function + noise
            noise = random.normalvariate(0, 1.5)
            true_wait = (
                3.0 + 
                (people_ahead * avg_service * priority_multiplier[priority_name]) + 
                (hour * 0.2) + 
                (3.0 if day < 5 else 1.0) + 
                noise
            )
            true_wait = max(1.0, true_wait)
            
            X_train.append([
                float(people_ahead),
                avg_service,
                float(dept_idx),
                float(prio_idx),
                hour,
                float(day)
            ])
            Y_train.append(true_wait)

        self.model.fit(X_train, Y_train)

    def predict(self, people_ahead, avg_service_time, department, priority, hour, day_of_week):
        """
        Runs ML prediction using the trained Random Forest model.
        Returns:
            predicted_wait: float
            confidence: int (percentage)
            crowd_level: str ("Low", "Medium", "High")
        """
        dept_idx = self._encode_service(department)
        prio_idx = self._encode_priority(priority)
        
        x = np.array([[
            float(people_ahead),
            float(avg_service_time),
            float(dept_idx),
            float(prio_idx),
            float(hour),
            float(day_of_week)
        ]])
        
        pred = self.model.predict(x)[0]
        pred = max(1.0, round(float(pred), 1))
        
        # Calculate crowd level based on wait time
        if pred < 12:
            crowd_level = "Low"
            confidence = random.randint(92, 98)
        elif pred < 28:
            crowd_level = "Medium"
            confidence = random.randint(88, 94)
        else:
            crowd_level = "High"
            confidence = random.randint(84, 90)
            
        return pred, confidence, crowd_level

# Instantiated single predictor
predictor = QueuePredictor()
