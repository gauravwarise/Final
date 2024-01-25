from django.contrib.sessions.models import Session
from django.utils import timezone


def is_user_logged_in(user):
    try:
        active_sessions = Session.objects.filter(
            expire_date__gte=timezone.now())
        for session in active_sessions:
            session_data = session.get_decoded()
            # print(session_data)
            if user.id == int(session_data.get('_auth_user_id')):
                return True
        return False
    except:
        return False


def deleteSession(client_id):
    try:
        active_sessions = Session.objects.filter(
            expire_date__gte=timezone.now())
        for session in active_sessions:
            session_data = session.get_decoded()
            if client_id == int(session_data.get('_auth_user_id')):
                session.delete()
                return True
        return False
    except:
        return False
