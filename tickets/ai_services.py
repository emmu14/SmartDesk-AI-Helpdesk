from ai_engine.predict import predict_category
from .models import Category

def get_predicted_category(description):
    result = predict_category(description)

    category = Category.objects.filter(
        name__iexact=result['category']
    ).first()

    return {
        'category': category,
        'confidence': result['confidence']
    }