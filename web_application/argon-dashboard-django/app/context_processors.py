from django.contrib.auth.models import User

def get_initials(request):
    current_user_name = request.user.username

    if current_user_name == 'dummy_user':
        return { 'initials': '-'} 

    elif len(current_user_name) > 0:
        return { 'initials': current_user_name[0]}
    
    else:
        return ''
