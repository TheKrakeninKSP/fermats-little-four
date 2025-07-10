from celery import shared_task
from .models import ARSession, ARTryOnResult
from .utils.ar_analytics import ARAnalytics
from .utils.ar_recommendations import ARRecommendationEngine
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_ar_session_result(session_id):
    """Process AR session results in background"""
    try:
        session = ARSession.objects.get(id=session_id)
        
        # Generate comprehensive analysis
        recommendation_engine = ARRecommendationEngine()
        
        # Get product recommendations
        recommendations = recommendation_engine.get_product_recommendations(
            session.user, session.product
        )
        
        # Update session with recommendations
        session.interaction_data['recommendations'] = [
            {'id': p.id, 'name': p.name, 'price': str(p.price)}
            for p in recommendations
        ]
        session.save()
        
        logger.info(f"Processed AR session {session_id} successfully")
        
    except ARSession.DoesNotExist:
        logger.error(f"AR session {session_id} not found")
    except Exception as e:
        logger.error(f"Error processing AR session {session_id}: {str(e)}")

@shared_task
def generate_ar_analytics_report():
    """Generate daily AR analytics report"""
    try:
        analytics = ARAnalytics()
        
        # Get performance metrics
        performance = analytics.get_product_performance()
        engagement = analytics.get_user_engagement_metrics()
        sizing = analytics.get_sizing_insights()
        
        # Store or send report
        report = {
            'date': timezone.now().date(),
            'performance': list(performance),
            'engagement': engagement,
            'sizing': sizing
        }
        
        # You could save this to a model, send via email, etc.
        logger.info("Generated AR analytics report successfully")
        
    except Exception as e:
        logger.error(f"Error generating AR analytics report: {str(e)}")
