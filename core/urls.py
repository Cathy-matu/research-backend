from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserMeView, ChangePasswordView, UserViewSet, ProjectViewSet, TaskViewSet, 
    PartnerViewSet, OutputViewSet, MessageViewSet, EventViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'partners', PartnerViewSet)
router.register(r'outputs', OutputViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'events', EventViewSet)

urlpatterns = [
    path('me/', UserMeView.as_view(), name='user-me'),
    path('users/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('', include(router.urls)),
]
