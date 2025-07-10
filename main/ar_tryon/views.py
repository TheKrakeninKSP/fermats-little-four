from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Product, ARModel, BodyMeasurement, ARSession, ARTryOnResult
from .serializers import (
    ProductSerializer, ARModelSerializer, BodyMeasurementSerializer,
    ARSessionSerializer, ARTryOnResultSerializer
)
import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def ar_tryon_page(request):
    ar_model = ARModel.objects.first()  # or use .get(product=...) etc.
    return render(request, 'ar_tryon.html', {'ar_model': ar_model})


class ARTryOnViewSet(viewsets.ModelViewSet):
    """Main AR try-on functionality"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ARModel.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        if self.action == 'start_session':
            return ARSessionSerializer
        return ARModelSerializer
    
    @action(detail=True, methods=['post'])
    def start_session(self, request, pk=None):
        """Start a new AR try-on session"""
        ar_model = get_object_or_404(ARModel, pk=pk)
        
        session = ARSession.objects.create(
            user=request.user,
            product=ar_model.product,
            interaction_data={}
        )
        
        # Get user measurements if available
        measurements = None
        if hasattr(request.user, 'body_measurements'):
            measurements = BodyMeasurementSerializer(request.user.body_measurements).data
        
        response_data = {
            'session_id': session.id,
            'ar_model': ARModelSerializer(ar_model).data,
            'user_measurements': measurements,
            'sizing_recommendations': self._get_sizing_recommendations(ar_model, measurements)
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def update_session(self, request):
        """Update AR session with interaction data"""
        session_id = request.data.get('session_id')
        session = get_object_or_404(ARSession, id=session_id, user=request.user)
        
        # Update interaction data
        interaction_data = request.data.get('interaction_data', {})
        session.interaction_data.update(interaction_data)
        session.save()
        
        return Response({'status': 'updated'})
    
    @action(detail=False, methods=['post'])
    def end_session(self, request):
        """End AR session and process results"""
        session_id = request.data.get('session_id')
        session = get_object_or_404(ARSession, id=session_id, user=request.user)
        
        # Process final data
        fit_rating = request.data.get('fit_rating')
        feedback = request.data.get('feedback', '')
        screenshot = request.FILES.get('screenshot')
        
        session.fit_rating = fit_rating
        session.feedback = feedback
        if screenshot:
            session.screenshot = screenshot
        session.save()
        
        # Generate try-on result
        result = self._generate_tryon_result(session, request.data)
        
        return Response({
            'session_id': session.id,
            'result': ARTryOnResultSerializer(result).data
        })
    
    def _get_sizing_recommendations(self, ar_model, measurements):
        """Generate sizing recommendations based on measurements"""
        if not measurements:
            return {'recommendation': 'Please add your measurements for better fitting'}
        
        # Simple sizing logic - you'd implement more sophisticated algorithms
        sizing_data = ar_model.sizing_data
        category = ar_model.category
        
        recommendations = {
            'suggested_size': 'M',  # Default
            'confidence': 0.5,
            'notes': []
        }
        
        # Basic sizing logic based on category
        if category == 'shirt' and measurements.get('chest'):
            chest = measurements['chest']
            if chest < 90:
                recommendations['suggested_size'] = 'S'
            elif chest < 100:
                recommendations['suggested_size'] = 'M'
            elif chest < 110:
                recommendations['suggested_size'] = 'L'
            else:
                recommendations['suggested_size'] = 'XL'
            recommendations['confidence'] = 0.8
        
        return recommendations
    
    def _generate_tryon_result(self, session, data):
        """Generate comprehensive try-on result"""
        # Calculate fit score based on various factors
        fit_score = self._calculate_fit_score(session, data)
        
        # Get size recommendation
        ar_model = session.product.ar_model
        measurements = getattr(session.user, 'body_measurements', None)
        sizing_rec = self._get_sizing_recommendations(ar_model, 
            BodyMeasurementSerializer(measurements).data if measurements else None)
        
        # Create result
        result = ARTryOnResult.objects.create(
            session=session,
            fit_score=fit_score,
            size_recommendation=sizing_rec['suggested_size'],
            fit_issues=data.get('fit_issues', []),
            color_match_score=data.get('color_match_score'),
            style_compatibility=data.get('style_compatibility')
        )
        
        # Add product recommendations
        recommended_products = self._get_product_recommendations(session.product, session.user)
        result.recommended_products.set(recommended_products)
        
        return result
    
    def _calculate_fit_score(self, session, data):
        """Calculate overall fit score"""
        base_score = 70  # Default score
        
        # Adjust based on user rating
        if session.fit_rating:
            base_score = session.fit_rating * 20  # Convert 1-5 to 20-100
        
        # Adjust based on measurements match
        if hasattr(session.user, 'body_measurements'):
            base_score += 10  # Bonus for having measurements
        
        # Adjust based on interaction time (engagement)
        if session.duration:
            if session.duration.total_seconds() > 30:
                base_score += 5  # Bonus for spending time
        
        return min(base_score, 100)
    
    def _get_product_recommendations(self, product, user):
        """Get related product recommendations"""
        # Simple recommendation - same category, different products
        return Product.objects.filter(
            category=product.category
        ).exclude(id=product.id)[:3]

class BodyMeasurementViewSet(viewsets.ModelViewSet):
    """Manage user body measurements"""
    serializer_class = BodyMeasurementSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return BodyMeasurement.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
