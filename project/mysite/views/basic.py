from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .utils import get_all_info, get_statistics_info, get_settings_info

@login_required
def get_user_info(request):
    user = request.user
    
    return JsonResponse(get_all_info(user))

@login_required
def get_statistics(request): 
    return JsonResponse(get_statistics_info(request.user))

@login_required
def get_settings(request):
    return JsonResponse(get_settings_info(request.user))