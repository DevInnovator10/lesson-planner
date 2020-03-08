from lesson_plans.models import UserProfile

def user_role_context(request):
    role = None
    if request.user.is_authenticated:

        try:
            role = request.user.userprofile.role
        except UserProfile.DoesNotExist:
            pass
    return {'user_role': role}
