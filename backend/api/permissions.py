from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsInstructorOrReadOnly(BasePermission):
    """
    Allows access only to instructors for non-safe methods.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.role == 'instructor'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        # Write permissions are only allowed to the instructor of the course.
        return obj.instructor == request.user
