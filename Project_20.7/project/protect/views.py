from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin 
from django.views.generic.edit import CreateView


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'protect/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_reguser'] = not self.request.user.groups.filter(name='reguser').exists()
        return context

class ForReguser(PermissionRequiredMixin, CreateView):
    permission_required = ('simpleapp.add_post',
                           'simpleapp.edit_post', 'simpleapp.delete_post',)