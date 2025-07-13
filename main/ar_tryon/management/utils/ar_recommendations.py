import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .models import ARSession, Product, BodyMeasurement

class ARRecommendationEngine:
    """AI-powered recommendation engine for AR try-on"""
    
    def __init__(self):
        self.size_mapping = {
            'XS': 0, 'S': 1, 'M': 2, 'L': 3, 'XL': 4, 'XXL': 5
        }
    
    def get_size_recommendation(self, product, user_measurements):
        """Get personalized size recommendation"""
        if not user_measurements:
            return {'size': 'M', 'confidence': 0.3, 'reason': 'No measurements available'}
        
        ar_model = getattr(product, 'ar_model', None)
        if not ar_model or not ar_model.sizing_data:
            return {'size': 'M', 'confidence': 0.3, 'reason': 'No sizing data available'}
        
        # Get user's key measurements
        user_chest = getattr(user_measurements, 'chest', None)
        user_waist = getattr(user_measurements, 'waist', None)
        
        best_size = 'M'
        best_score = 0
        
        for size, measurements in ar_model.sizing_data.items():
            score = self._calculate_fit_score(
                user_measurements, measurements, ar_model.category
            )
            
            if score > best_score:
                best_score = score
                best_size = size
        
        confidence = min(best_score, 0.95)  # Cap at 95%
        
        return {
            'size': best_size,
            'confidence': confidence,
            'reason': f'Based on your measurements and fit analysis'
        }
    
    def _calculate_fit_score(self, user_measurements, size_measurements, category):
        """Calculate how well a size fits the user"""
        score = 0.5  # Base score
        
        if category == 'shirt':
            if hasattr(user_measurements, 'chest') and 'chest' in size_measurements:
                chest_diff = abs(user_measurements.chest - size_measurements['chest'])
                # Ideal fit is within 5cm
                if chest_diff <= 5:
                    score += 0.3
                elif chest_diff <= 10:
                    score += 0.15
                
        elif category == 'pants':
            if hasattr(user_measurements, 'waist') and 'waist' in size_measurements:
                waist_diff = abs(user_measurements.waist - size_measurements['waist'])
                if waist_diff <= 3:
                    score += 0.3
                elif waist_diff <= 6:
                    score += 0.15
        
        return score
    
    def get_product_recommendations(self, user, current_product, limit=5):
        """Get personalized product recommendations"""
        # Get user's AR session history
        user_sessions = ARSession.objects.filter(user=user).select_related('product')
        
        if not user_sessions.exists():
            # New user - recommend popular items
            return Product.objects.filter(
                category=current_product.category
            ).exclude(id=current_product.id)[:limit]
        
        # Get user preferences from past sessions
        liked_products = user_sessions.filter(fit_rating__gte=4).values_list('product_id', flat=True)
        
        # Find similar products
        similar_products = Product.objects.filter(
            category=current_product.category
        ).exclude(id=current_product.id)
        
        # Simple collaborative filtering
        recommendations = []
        for product in similar_products:
            similarity_score = self._calculate_product_similarity(
                current_product, product, list(liked_products)
            )
            recommendations.append((product, similarity_score))
        
        # Sort by similarity score
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return [product for product, score in recommendations[:limit]]
    
    def _calculate_product_similarity(self, product1, product2, user_liked_products):
        """Calculate similarity between two products"""
        score = 0
        
        # Same category bonus
        if product1.category == product2.category:
            score += 0.5
        
        # User preference bonus
        if product2.id in user_liked_products:
            score += 0.3
        
        # Price similarity
        price_diff = abs(product1.price - product2.price)
        if price_diff < 20:
            score += 0.2
        
        return score