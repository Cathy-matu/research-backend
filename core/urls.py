from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserMeView, ChangePasswordView, UserViewSet, ProjectViewSet, TaskViewSet, 
    PartnerViewSet, OutputViewSet, MessageViewSet, EventViewSet,
    InnovatorViewSet, IdeaViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'partners', PartnerViewSet, basename='partner')
router.register(r'outputs', OutputViewSet, basename='output')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'events', EventViewSet, basename='event')
router.register(r'innovator', InnovatorViewSet, basename='innovator')
router.register(r'idea', IdeaViewSet, basename='idea')

urlpatterns = [
    path('me/', UserMeView.as_view(), name='user-me'),
    path('users/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('', include(router.urls)),
]
