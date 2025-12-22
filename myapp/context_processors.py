from django.utils.functional import SimpleLazyObject

def _get_user_classes(user):
    try:
        if not user.is_authenticated:
            return []

        if hasattr(user, 'profile') and user.profile.role == 'teacher':
            return user.classes_created.all()
        else:
            return user.classes_joined.all()
    except Exception:
        # In case migrations haven't run or DB issues, fail gracefully.
        return []


def user_classes(request):
    """Context processor that injects `classes` into every template.

    Returns a queryset or empty list. Uses SimpleLazyObject to avoid
    querying the DB when not needed by the template rendering.
    """
    return {
        'classes': SimpleLazyObject(lambda: _get_user_classes(request.user))
    }
