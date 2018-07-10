from django.db import models
from django.conf.urls import url
from console import views
from django.urls import path


# Create your models here.
urlpatterns = [
    path('', views.index, name='index'),
    url(r'^availability/display/(?P<name>[\w@%.]+)/$', views.display_availability, name='display_availability'),
    url(r'^settings/$', views.save_credentials, name='save_credentials'),
    url(r'^settings/credentials/$', views.save_credentials, name='save_credentials'),
    url(r'^settings/githubRepository/$', views.save_github_repo, name='save_github_repo'),

    url(r'^settings/local/directory/$', views.save_local_directory, name='save_local_directory'),
    url(r'^data/empty/folder/delete/$', views.delete_empty_folders, name='delete_empty_folders'),
    url(r'^data/$', views.display_data_folders, name='data_folders'),
    url(r'^job/create/$', views.create_job, name='create_job'),
    url(r'^jobs/$', views.list_jobs, name='list_jobs'),
    url(r'^jobs/success/$', views.list_jobs_success, name='list_jobs_success'),
    url(r'^settings/controllers/$', views.save_controller_settings, name='save_controller_settings'),
    url(r'^jobs/(?P<message>[\w@%.]+)/$', views.list_jobs, name='list_jobs'),
    url(r'^get_car_status_autopilot/$', views.get_car_status_autopilot, name='get_car_status_autopilot'),
    url(r'^get_car_status_training/$', views.get_car_status_training, name='get_car_status_training'),
    url(r'^home/$', views.home, name='home'),
    url(r'^data/download/$', views.getfiles, name='getfiles'),
    url(r'^data/delete/$', views.delete_data, name='delete_data'),
    url(r'^job/remark/delete/$', views.delete_remark, name='delete_remark'),
    url(r'^job/remark/add/$', views.add_remark, name='add_remark'),
    url(r'^job/delete/$', views.delete_job, name='delete_job'),
    url(r'^model/local/copy/$', views.copy_local, name='copy_local'),
    url(r'^autopilot/$', views.autopilot, name='autopilot'),
    url(r'^proc/kill/$', views.kill_proc, name='kill_proc'),
    path('availability/display/', views.display_availability, name='display'),
    url(r'^status/update/id/$', views.update_status_by_id, name='update_status_by_id'),
    url(r'^request/cancel/$', views.cancel_request, name='cancel_request'),
    url(r'^data/comment/add/$', views.add_data_folder_comment, name='add_data_folder_comment'),
    url(r'^data/comment/delete/$', views.delete_data_folder_comment, name='delete_data_folder_comment'),
    path('drive/', views.drive, name='drive'),

]