from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .utils import get_all_info

#================================================================================= PROFILE PAGE ===================================================================================================================

@login_required
def profile_page(request):
    return render(request, 'app_site/profile.html', context = {
        'app_name': 'app_site',
        'page_name': 'profile',
                                                      'user_info': get_all_info(request.user),
                                                    })

#--------------------------------------------------------------------------- PROFILE PAGE - CHANGE SETTINGS
@require_POST
@login_required
def change_settings(request):
    user = request.user
    instance_type = request.POST.get('instance_type')
    print(f'------ SETTINGS CHANGING ---> instance type = {instance_type}')
    instance_language = request.POST.get('instance_language')
    print(f'------ SETTINGS CHANGING ---> instance language = {instance_language}')

    dict_key = f"{instance_type}_{instance_language}"
    settings = user.settings.dictionaries.get(dict_key, {})

    def to_int(value, default=None):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    new_settings = {
        'study_list_length': to_int(request.POST.get('study_list_length'), 20),
        'repeat_words_number': to_int(request.POST.get('repeat_words_number'), 10),
        # 'box_1_limit': to_int(request.POST.get('BOX_1_limit'), 90),
        # 'box_2_limit': to_int(request.POST.get('BOX_2_limit'), 150),
        # 'box_3_limit': to_int(request.POST.get('BOX_3_limit'), 150),
        # 'testing_days_limit': to_int(request.POST.get('testing_days_limit'), 5),
    }

    settings.update(new_settings)
    user.settings.dictionaries[dict_key] = settings  # <-- зберігаємо назад
    user.settings.save()

    return redirect('/profile/')