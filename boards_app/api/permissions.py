from rest_framework import permissions

class IsBoardOwnerOrMember(permissions.BasePermission):
    """
    Custom permission to only allow board owners or members to access the board.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Allow if user is owner or member
        return obj.owner == request.user or request.user in obj.members.all()


class IsBoardOwner(permissions.BasePermission):
    """
    Custom permission to only allow board owners to edit/delete the board.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions for members
        if request.method in permissions.SAFE_METHODS:
            return obj.owner == request.user or request.user in obj.members.all()
        
        # Write permissions only for owner
        return obj.owner == request.user
    
class IsTaskBoardMember(permissions.BasePermission):
    """
    Custom permission to only allow board members to access tasks.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Check if user is owner or member of the task's board
        board = obj.board if hasattr(obj, 'board') else obj.task.board
        return board.owner == request.user or request.user in board.members.all()


    
class IsTaskAssignee(permissions.BasePermission):
    """
    Custom permission to only allow task assignees to edit certain fields.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Allow board members to edit, but restrict some actions
        board = obj.board
        is_board_member = board.owner == request.user or request.user in board.members.all()
        
        return is_board_member