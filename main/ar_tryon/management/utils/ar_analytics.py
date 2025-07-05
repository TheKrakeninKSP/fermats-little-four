from django.db.models import Avg, Count, F
from django.utils import timezone
from datetime import timedelta
from .models import ARSession, ARTryOnResult, Product

class ARAnalytics:
    """Analytics utilities for AR try-on data"""
    
    @staticmethod
    def get_product_performance(product_id=None, days=30):
        """Get AR performance metrics for products"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        queryset = ARSession.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        return queryset.values('product__name').annotate(
            total_sessions=Count('id'),
            avg_fit_rating=Avg('fit_rating'),
            avg_duration=Avg('duration'),
            conversion_rate=Count('id', filter=F('fit_rating__gte=4')) * 100.0 / Count('id')
        ).order_by('-total_sessions')
    
    @staticmethod
    def get_sizing_insights(category=None):
        """Get insights about size recommendations vs actual selections"""
        queryset = ARTryOnResult.objects.all()
        
        if category:
            queryset = queryset.filter(session__product__category=category)
        
        return {
            'size_accuracy': queryset.filter(
                size_recommendation=F('session__interaction_data__selected_size')
            ).count() / queryset.count() * 100,
            'most_recommended_sizes': queryset.values('size_recommendation').annotate(
                count=Count('id')
            ).order_by('-count'),
            'fit_score_by_size': queryset.values('size_recommendation').annotate(
                avg_fit_score=Avg('fit_score')
            ).order_by('-avg_fit_score')
        }
    
    @staticmethod
    def get_user_engagement_metrics(days=30):
        """Get user engagement metrics"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        sessions = ARSession.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        return {
            'total_sessions': sessions.count(),
            'unique_users': sessions.values('user').distinct().count(),
            'avg_session_duration': sessions.aggregate(
                avg_duration=Avg('duration')
            )['avg_duration'],
            'completion_rate': sessions.filter(
                fit_rating__isnull=False
            ).count() / sessions.count() * 100,
            'high_satisfaction_rate': sessions.filter(
                fit_rating__gte=4
            ).count() / sessions.count() * 100
        }
