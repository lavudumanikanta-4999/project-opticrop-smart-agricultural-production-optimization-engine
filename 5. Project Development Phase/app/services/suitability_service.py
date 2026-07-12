import logging
from app.models.input_vector import InputVector
from app.models.suitability_result import SuitabilityResult

logger = logging.getLogger(__name__)

class SuitabilityService:
    def __init__(self, config) -> None:
        self.thresholds = config.SUITABILITY_THRESHOLDS if hasattr(config, 'SUITABILITY_THRESHOLDS') else {}
        
    def evaluate(self, input_vector: InputVector) -> SuitabilityResult:
        suitable = []
        marginal = []
        unsuitable = []
        
        # Example threshold structure in config:
        # {
        #   "rice": {
        #       "N": {"min": 60, "max": 100},
        #       "P": {"min": 30, "max": 60},
        #       ...
        #   }
        # }
        # Evaluation logic: 
        # If all 7 features are within [min, max], it's suitable.
        # If <= 2 features are slightly out of bounds (say within 15% margin), it's marginal.
        # Otherwise, unsuitable.
        # Note: if thresholds are missing, everything might be unsuitable.
        
        for crop, bounds in self.thresholds.items():
            out_of_bounds_count = 0
            marginal_count = 0
            
            for feature in ['N', 'P', 'K', 'temperature', 'humidity', 'rainfall', 'ph']:
                val = getattr(input_vector, feature)
                if feature in bounds:
                    f_min = bounds[feature].get('min', 0)
                    f_max = bounds[feature].get('max', 9999)
                    
                    if not (f_min <= val <= f_max):
                        # check if within 15% margin
                        margin = 0.15 * (f_max - f_min) if f_max != f_min else 0.15 * f_min
                        if (f_min - margin) <= val <= (f_max + margin):
                            marginal_count += 1
                        else:
                            out_of_bounds_count += 1
                            
            if out_of_bounds_count == 0 and marginal_count == 0:
                suitable.append(crop)
            elif out_of_bounds_count == 0 and marginal_count <= 2:
                marginal.append(crop)
            else:
                unsuitable.append(crop)
                
        return SuitabilityResult(
            suitable=suitable,
            marginal=marginal,
            unsuitable=unsuitable
        )
