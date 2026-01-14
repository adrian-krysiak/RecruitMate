from django.urls import path
from .views import AnalyzeMatchView, GenerateCvView, AdviceCareerView


app_name = 'advisor'

urlpatterns = [
    path('analyze/match/', AnalyzeMatchView.as_view(), name='analyze_match'),
    path('generate/cv/', GenerateCvView.as_view(), name='generate_cv'),
    path('advice/career/', AdviceCareerView.as_view(), name='career_advice'),
]
