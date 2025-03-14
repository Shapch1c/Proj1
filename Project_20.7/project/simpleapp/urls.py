from django.urls import path
from .views import PostsList, PostsDetail, PostsSearch, PostsCreate, PostsUpdate, PostsDelete, IndexView, Index
from django.views.decorators.cache import cache_page
from .views import user_responses, accept_response, delete_response, create_response, index, register_view, verify_email_view, send_mass_email
urlpatterns = [
    path('', cache_page(60)(PostsList.as_view()), name='post_list'),
    # path('', IndexView.as_view()),
    path('search/', cache_page(300)(PostsSearch.as_view()), name='search'),
    path('<int:pk>/', PostsDetail.as_view(), name='post_detail'),
    path('create/', PostsCreate.as_view(), name='post_create'),
    path('<int:pk>/edit/', PostsUpdate.as_view(), name='post_edit'),
    path('<int:pk>/delete/', PostsDelete.as_view(), name='post_delete'),
    path('responses/', user_responses, name='user_responses'),
    path('response/create/<int:post_id>/', create_response, name='create_response'),
    path('response/<int:response_id>/accept/', accept_response, name='accept_response'),
    path('response/<int:response_id>/delete/', delete_response, name='delete_response'),
    path('', index, name='index'),
    path("register/", register_view, name="register"),
    path("verify/", verify_email_view, name="verify"),
    path('send-mass-email/', send_mass_email, name='send_mass_email'),
]



