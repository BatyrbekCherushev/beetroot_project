
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.shortcuts import render

from .utils import get_all_info

#======================================================================================= ARMORY PAGE =======================================================================================
@login_required
def armory_page(request):
    return render(request, 'armory.html', context = {'page_name': 'armory',

                                                     'user_info': get_all_info(request.user),})