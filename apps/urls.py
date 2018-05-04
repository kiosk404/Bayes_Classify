from . import views
from django.urls import path

urlpatterns = [
    path('',views.index_view,name='index'),
    path('workstation.html',views.workstation_view,name='workstation'),
    path('run_spider.html',views.run_spider_view,name='run_spider_html'),
    path('check.html',views.check_view,name='check'),
    path('check_csdn.html',views.check_csdn_view,name='check_csdn'),
    path('category.html',views.category_view,name='category'),


    path('run_sipder',views.run_spider,name='run_spider'),
    path('run_check',views.run_check,name='run_check'),
    path('run_check_csdn',views.run_check_csdn,name='run_check_csdn'),
    path('run_create_category',views.run_create_category,name='run_create_category'),
    path('run_get_category',views.run_get_category,name='run_get_category')
]