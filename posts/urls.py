from django.urls import path

from .views import PostsListApiView, PostDetailMobileApiView, PostDetailDesktopApiView, CreatePostApiView, HomePagePostsApiView, GetLikesApiView, GetCommentsApiView, CreateSavedPostApiView, SavedPostsListApiView, PostLikeApiView, PostCommentApiView, CommentLikeApiView, CommentDeleteApiView, UpdatePostApiView, DeletePostApiView, PostsFeedsApiView

app_name = 'posts'

urlpatterns = [
        path('list/<slug:username>/', PostsListApiView.as_view()),
        path('feeds/<slug:username>/', PostsFeedsApiView.as_view()),
        path('post/like/', PostLikeApiView.as_view()),
        path('post/comment/', PostCommentApiView.as_view()),
        path('comment/like/', CommentLikeApiView.as_view()),
        path('comment/delete/', CommentDeleteApiView.as_view()),
        path('save/', CreateSavedPostApiView.as_view()),
        path('saved/', SavedPostsListApiView.as_view()),
        path('<slug>/liked_by/', GetLikesApiView.as_view()),
        path('<slug>/comments/', GetCommentsApiView.as_view(), name='post-comments'),
        path('create/', CreatePostApiView.as_view()),
        path('update/', UpdatePostApiView.as_view()),
        path('delete/<slug>/', DeletePostApiView.as_view()),
        path('feeds/', HomePagePostsApiView.as_view()),
        path('d/<slug>/', PostDetailDesktopApiView.as_view()),
        path('<slug>/', PostDetailMobileApiView.as_view()),
]