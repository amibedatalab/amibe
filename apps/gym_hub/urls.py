from django.urls import path
from .views import (upload_master_file,
    upload_due_blue_book, upload_collection_flag,ApprovalDataListView,
      MasterVIewLIstView, BlueDueListView, ChannelPartnerListView,stream_commission_slab_view_data,
        approve_action, reject_action,stream_bb_db_view_data)

urlpatterns = [
    #upload section
    path('upload_master_file/', upload_master_file, name='upload_master_file'),
    path('upload_due_blue_book/', upload_due_blue_book, name='upload_due_blue_book'),
    path('upload_collection_flag/', upload_collection_flag,name="upload_collection_flag"),
    #download format
    #class view pages
    path('approval_fun/', ApprovalDataListView.as_view(),name="approval_fun"),
    path('master_view_report/', MasterVIewLIstView.as_view(),name='master_view_report'),
    path('due_blue_view_report/', BlueDueListView.as_view(),name='due_blue_view_report'),
    path('channel_partner_records/', ChannelPartnerListView.as_view(),name='channel_partner_records'),
    #approve or reject functionality
    path('approve/<int:header_id>/<int:data_id>/', approve_action, name='approve_action'),
    path('reject/<int:header_id>/<int:data_id>/', reject_action, name='reject_action'),
    #download view page of commission and DB BB data.
    path('stream_commission_slab_view_data/', stream_commission_slab_view_data, name='stream_commission_slab_view_data'),
    path('stream_bb_db_view_data/', stream_bb_db_view_data, name='stream_bb_db_view_data'),    
    ]
