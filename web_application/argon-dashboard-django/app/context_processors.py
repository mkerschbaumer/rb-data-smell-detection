from django.contrib.auth.models import User

def get_initials(request):
    current_user_name = request.user.username

    if current_user_name == 'dummy_user':
        return { 'initials': '-'} 

    elif len(current_user_name) > 0:
        return { 'initials': request.user.first_name[0]+request.user.last_name[0]}
    
    else:
        return ''
