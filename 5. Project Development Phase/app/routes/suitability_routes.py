from flask import Blueprint, render_template, current_app
from app.extensions import limiter

suitability_bp = Blueprint('suitability_bp', __name__)

@suitability_bp.route('/suitability', methods=['GET'])
def suitability_page():
    return render_template('suitability.html')

def get_suitability_limit():
    return current_app.config.get('SUITABILITY_RATE_LIMIT', '20 per minute')

@suitability_bp.route('/api/suitability', methods=['POST'])
@limiter.limit(get_suitability_limit)
def api_suitability():
    from app.controllers.suitability_controller import SuitabilityController
    from app.services.suitability_service import SuitabilityService
    
    service = SuitabilityService(current_app.config)
    controller = SuitabilityController(service)
    
    return controller.handle_suitability()
