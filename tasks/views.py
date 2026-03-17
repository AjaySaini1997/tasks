from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Task
from .serializers import TaskSerializer, TaskCreateSerializer
from .permissions import IsOwnerOrAdmin
from .filters import TaskFilter


class TaskListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/tasks/      - List all tasks (authenticated user sees own tasks)
    POST /api/tasks/      - Create a new task
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Task.objects.all()
        return Task.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCreateSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @swagger_auto_schema(
        operation_description="Get list of all tasks. Admin sees all, users see their own.",
        manual_parameters=[
            openapi.Parameter('completed', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, description='Filter by completion'),
            openapi.Parameter('priority', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Filter by priority: low/medium/high'),
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page number'),
        ],
        responses={200: TaskSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new task.",
        request_body=TaskCreateSerializer,
        responses={201: TaskSerializer, 400: 'Validation Error'}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/tasks/{id}/ - Get task details
    PUT    /api/tasks/{id}/ - Update a task
    PATCH  /api/tasks/{id}/ - Partially update a task
    DELETE /api/tasks/{id}/ - Delete a task
    """
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    serializer_class = TaskSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Task.objects.all()
        return Task.objects.filter(owner=self.request.user)

    @swagger_auto_schema(responses={200: TaskSerializer, 404: 'Not Found'})
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(request_body=TaskSerializer, responses={200: TaskSerializer})
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(request_body=TaskSerializer, responses={200: TaskSerializer})
    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(responses={204: 'Deleted', 403: 'Forbidden'})
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
