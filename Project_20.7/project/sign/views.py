from django.contrib.auth.models import User
from django.views.generic.edit import CreateView
from .models import BaseRegisterForm
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required

class BaseRegisterView(CreateView):
    model = User
    form_class = BaseRegisterForm
    success_url = '/'


@login_required
def upgrade_me(request):
    user = request.user
    reguser_group = Group.objects.get(name='reguser')
    if not request.user.groups.filter(name='reguser').exists():
        reguser_group.user_set.add(user)
    return redirect('/account/')



