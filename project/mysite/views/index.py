from django.contrib.auth.decorators import login_required
from django.shortcuts import render
#========================================================================================= INDEX PAGE =====================================================================================
@login_required
def index_page(request):
    return render(request, 'index.html', context = {'page_name': 'index',
                                                    'user_name': request.user.username})