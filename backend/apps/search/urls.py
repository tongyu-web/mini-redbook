from django.urls import path
from . import views

urlpatterns = [
    path("", views.SearchView.as_view(), name="search"),
    path("suggest/", views.SuggestView.as_view(), name="suggest"),
    path("hot-tags/", views.HotTagView.as_view(), name="hot-tags"),
    path("hot-search/", views.HotSearchView.as_view(), name="hot-search"),
    path("recommend/", views.RecommendView.as_view(), name="recommend"),
    path("history/", views.SearchHistoryView.as_view(), name="search-history"),
]
