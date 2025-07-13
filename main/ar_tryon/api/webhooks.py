from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def ar_model_update_webhook(request):
    """Webhook for AR model updates from 3D modeling service"""
    try:
        data = json.loads(request.body) 
        # Process AR model update
        model_id = data.get('model_id')
        status = data.get('status')
        if status == 'completed':
            # Update AR model with new files
            ar_model = ARModel.objects.get(id=model_id)
            ar_model.is_active = True
            ar_model.save()            
            logger.info(f"AR model {model_id} updated successfully")   
        return HttpResponse(status=200)     
    except Exception as e:
        logger.error(f"AR model webhook error: {str(e)}")
        return HttpResponse(status=500)