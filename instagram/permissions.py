from rest_framework import permissions


class IsAuthorOrReadonly(permissions.BasePermission):
    # 인증된사람만 목록조회, 새 포스팅등록 가능
    def has_permisstion(self, request, view):
        return request.user and request.user.is_authenticated

    
    def has_object_permission(self, request, views, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.author == request.user
