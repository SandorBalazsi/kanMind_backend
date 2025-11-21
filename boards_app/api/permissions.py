"""Permission classes for board, task, and comment access control.

Defines fine-grained permission checks to ensure users can only access
boards, tasks, and comments they are authorized to view or modify.
"""

from rest_framework import permissions

class IsBoardOwnerOrMember(permissions.BasePermission):
    """Permission to access a board if user is the owner or a member.

    Requires authentication and checks if the user is either the board owner
    or a member of the board.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Allow if user is owner or member
        return obj.owner == request.user or request.user in obj.members.all()


class IsBoardOwner(permissions.BasePermission):
    """Permission for board-specific access control.

    Read access is allowed for board owner and members.
    Write access is restricted to board owner only.
    """
 
    def has_object_permission(self, request, view, obj):
        # Read permissions for members
        if request.method in permissions.SAFE_METHODS:
            return obj.owner == request.user or request.user in obj.members.all()
        
        # Write permissions only for owner
        return obj.owner == request.user
    
    
class IsTaskBoardMember(permissions.BasePermission):
    """Permission to access a task if user is a member of its board.

    Requires authentication and checks if the user is either the board owner
    or a member of the task's board.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Check if user is owner or member of the task's board
        board = obj.board if hasattr(obj, 'board') else obj.task.board
        return board.owner == request.user or request.user in board.members.all()



class IsTaskAssignee(permissions.BasePermission):
    """Permission for task editing by board members.

    Allows all read operations for any authenticated user.
    Restricts write operations to board owner and members.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Allow board members to edit, but restrict some actions
        board = obj.board
        is_board_member = board.owner == request.user or request.user in board.members.all()
        
        return is_board_member