from .tasks import (save_commision_slab_rate_task,download_view_data,
                    save_error_table,update_collection_flag,
                    save_blue_due_book_task)
from datetime import datetime
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator
from django.views.generic.list import ListView
from django.contrib import messages
import time
import pytz
indian_tz = pytz.timezone('Asia/Kolkata')
import logging
from django.http import FileResponse
from babel.numbers import format_decimal
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from apps.gym_hub.forms import (
    FileUploadCollectionFlagForm,
    FileIUploadForm,
    FileUploadMasterForm, ApprovalForm, RejectionForm
)
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from apps.authentication.templatetags.user_permissions import \
    user_has_permission
from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend
import pandas as pd
from urllib.parse import urlencode
from .models import (
    TempTableBB,
    MasterRate,
    DataUploadTask,
    TempTable, UploadBlueBook, UploadDueBook, ApprovalData,
    CollectionUpdate, ChannelPartner
)
import io
from django.db.models import Q
logger = logging.getLogger(__name__)

def approve_action(request, header_id, data_id):
    header = ApprovalData.objects.get(pk=header_id)
    model_instance = ApprovalData.objects.get(pk=header_id)
    excel_file = model_instance.file.path
    df=pd.read_excel(excel_file)
    blue_df = df[df['book_type'] == "BB"]
    due_df = df[df['book_type'] == "DB"]
    if due_df.shape[0] != 0:
        due_df = due_df.to_dict(orient="records")
        model_obj = [TempTable(**row) for row in due_df]
        try:
            TempTable.objects.bulk_create(model_obj)
        except Exception as e:
            logging.info("the error--",e)
            
    if blue_df.shape[0] != 0:
        blue_df = blue_df.to_dict(orient="records")
        model_obj = [TempTableBB(**row) for row in blue_df]
        try:
            TempTableBB.objects.bulk_create(model_obj)
        except Exception as e:
            logging.info("the error--",e)
    if request.method == 'POST':
        form = ApprovalForm(request.POST)
        if form.is_valid():
            # Update the 'is_approved' field and save the model
            header.is_approved = True
            header.approved_on = datetime.now()
            dataupload = DataUploadTask.objects.filter(pk=data_id)
            dataupload_action=DataUploadTask.objects.values('action').filter(pk=data_id).first()
            dataupload.update(is_approved=True, approved_by=str(request.user),
                              approved_on=datetime.now(),
                              status="Data has been approved")
            header.save()
            save_blue_due_book_task.delay(data_id)
            # if dataupload_action or dataupload_action['action'] == "APPEND":
            #     save_blue_due_book_task.delay(data_id)           
            
            return redirect(reverse('approval_fun'))

def reject_action(request, header_id, data_id):
    dataupload = DataUploadTask.objects.get(pk=data_id)
    if request.method == 'POST':
        form = RejectionForm(request.POST)
        if form.is_valid():
            rejection_message = form.cleaned_data['rejection_message']
            #logging.info(rejection_message)
            model_obj = ApprovalData.objects.filter(id=header_id)
            model_obj.update(message=rejection_message, is_approved=False,approved_on=datetime.now())
            dataupload = DataUploadTask.objects.filter(pk=data_id)
            dataupload.update(is_approved=False, approved_by=str(request.user),
                              approved_on=datetime.now(),
                              status=f"Data has been rejected -Reason- {rejection_message}")
            return redirect(reverse('approval_fun'))
    else:
        return redirect(reverse('approval_fun'))


class ApprovalDataListView(UserPassesTestMixin, ListView):
    model = ApprovalData
    template_name = "home/approval_page.html"
    context_object_name = "approver_table"
    paginate_by = 10
    
    @method_decorator(login_required(login_url=reverse_lazy('login')))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = ApprovalData.objects.all().order_by('-id')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = self.get_queryset()
        paginator = Paginator(items, self.paginate_by)
        page_number = self.request.GET.get('page')
        page = paginator.get_page(page_number)
        context['page'] = page
        return context

    def test_func(self):
        return user_has_permission(self.request.user, 'chsbc_hub.view_approverpermission')

    def handle_no_permission(self):
        error_message = "You don't have permission to access this page."
        return render(
            self.request,
            '403_forbidden.html',
            {'error_message': error_message},
            status=403
        )


class DataUploadTaskListView(UserPassesTestMixin, ListView):
    model = DataUploadTask  # Your model
    template_name = "home/first_view.html"  # Your template name
    # Optional: Set the context variable name
    context_object_name = "data_upload_task_table"
    # ordering = ["-id"]  # Optional: Set the ordering of the queryset
    paginate_by = 10

    @method_decorator(login_required(login_url=reverse_lazy('login')))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = DataUploadTask.objects.all().order_by("-id")
        self.file_type = self.request.GET.get('file_type')
        self.financial_year = self.request.GET.get('financial_year')
        self.is_approved = self.request.GET.get('is_approved')
        self.status = self.request.GET.get('status')
        self.action = self.request.GET.get('action')
        if self.file_type:
            queryset = queryset.filter(file_type__istartswith=self.file_type)
        if self.financial_year:
            queryset = queryset.filter(
                financial_year__icontains=self.financial_year)
        if self.action:
            queryset = queryset.filter(action__istartswith=self.action)
        if self.status:
            queryset = queryset.filter(status__istartswith=self.status)
        if self.is_approved:
            queryset = queryset.filter(
                is_approved__istartswith=self.is_approved)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = self.get_queryset()
        paginator = Paginator(items, self.paginate_by)
        page_number = self.request.GET.get('page')
        page = paginator.get_page(page_number)
        context['page'] = page
        # Create a dictionary of filter parameters for dynamic pagination links
        filter_params = {
            'file_type': self.file_type,
            'financial_year': self.financial_year,
            'is_approved': self.is_approved,
            'status': self.status,
            'action': self.action,
        }
        context['filter_params'] = filter_params
        return context

    def test_func(self):
        return user_has_permission(self.request.user, 'chsbc_hub.view_fileupload')

    def handle_no_permission(self):
        error_message = "You don't have permission to access this page."
        return render(
            self.request,
            '403_forbidden.html',
            {'error_message': error_message},
            status=403
        )


def to_excel_no_date_conversion(data):
    df = pd.DataFrame(data)
    excel_file = io.BytesIO()
    xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
    df.to_excel(xlwriter, 'Sheet1', index=False)
    xlwriter.save()
    excel_file.seek(0)
    return excel_file

@login_required(login_url="login")
def upload_master_file(request):
    global_start_time = time.time()
    global_start_datetime = datetime.now()
    master_form=FileUploadMasterForm()
    if request.method == "POST":
        master_form = FileUploadMasterForm(request.POST, request.FILES)
        data_upload_task_table = DataUploadTask.objects.filter(
            file_type="COMMISSION_SLAB_MASTER").order_by('-id')
        if master_form.is_valid():
            file = request.FILES["file"]
            created_by = request.user
            file_type = "COMMISSION_SLAB_MASTER"
            action = master_form.cleaned_data.get("action")
            file_extension = file.name.split('.')[-1]
            if file_extension!='xlsx':
                logger.info("the uploaded file for master slab is not .xlsx")
                messages.success(request,"Please upload excel file only, use extention '.xlsx'")
                return redirect(upload_master_file)
            df = pd.read_excel(file, engine='openpyxl')
            if action=="APPEND":
                model_obj=MasterRate.objects.all().count()
                if model_obj == 0:
                    logger.info("Data not found in commission slab, there is zero record in commission slab, user need to uploade new file first")
                    messages.success(
                    request, "Data not found, please upload first, then append")
                    return redirect(upload_master_file)
                try:
                    df['Rate'] = df['Rate'].str.split('%')[0].str.strip()
                except Exception as e:
                    logger.info(f"The error whiel stripping the rate colun while uploading- {e}")
                total_records = df.shape[0]
                logger.info()
                df.columns = df.columns.str.lower()
                col_map = {"staff_non_staff": "is_staff"}
                df.rename(columns=col_map,inplace=True)                
                model_df = pd.DataFrame(MasterRate.objects.all().values())
                fields = MasterRate._meta.get_fields()
                field_name = [field.name for field in fields]
                model_df = pd.DataFrame(columns=field_name)
                excepts_cols = ['id', 'created_by', 'created_on', 'modified_on','is_active',
                                'modified_by', 'approved_by', 'approved_on', 'is_approved', 'data_id','action']
                model_df.drop(columns=excepts_cols, axis=1, inplace=True)
                #logging.info(model_df.columns)
                #logging.info(df.columns)
                if not model_df.columns.equals(df.columns):
                    messages.success(
                        request, "Either the columns name or columns order \
                        are not matching, Please download the format for the same.")
                    return redirect(upload_master_file)
                null_df = df.isnull().any(axis=1).sum()
                excel_file = io.BytesIO()
                if null_df != 0:
                    null_nan_mask = df.isnull() | df.isna()
                    null_nan_df = df[null_nan_mask.any(axis=1)]
                    with pd.ExcelWriter(excel_file, engine='xlsxwriter', mode='xlsx') as writer:
                        null_nan_df.to_excel(writer, index=False)
                excel_file.seek(0)
                valid_records = total_records - null_df
                invalid_records = null_df
                df = df.dropna()
                logger.info("the executing time in checking shape",
                            time.time() - global_start_time)
                task_end_time = datetime.now()
                datauploadobj = DataUploadTask( created_by=str(created_by), total_records=total_records,
                    error_records=invalid_records,
                    action=action, file_type=file_type, started_at=global_start_datetime,
                    ended_at=task_end_time,approved_by=None,approved_on=None,is_approved=None, status="Uploaded..",
                    valid_records=valid_records, file=file,
                )
                if null_df != 0:
                    datauploadobj.error_file.save('error_data.xlsx', excel_file)
                datauploadobj.save()
                logger.info("the executing time in populate the data upload task table",
                            time.time() - global_start_time)
                # latest_id=DataUploadTask.objects.latest('id').id
                # df['data_id']=latest_id
                data_json = df.to_dict(orient='records')
                save_commision_slab_rate_task.delay(data_json)
                
                messages.success(
                    request, "The Commission Slab has been uploaded.")
                return redirect(upload_master_file)
            else:
                
                total_records = df.shape[0]
                df.columns = df.columns.str.lower()
                col_map = {"staff_non_staff": "is_staff"}
                df.rename(columns=col_map,inplace=True)
                model_df = pd.DataFrame(MasterRate.objects.all().values())
                fields = MasterRate._meta.get_fields()
                field_name = [field.name for field in fields]
                model_df = pd.DataFrame(columns=field_name)
                excepts_cols = ['id', 'created_by', 'created_on', 'modified_on','is_active',
                                'modified_by', 'approved_by', 'approved_on', 'is_approved', 'data_id','action']
                model_df.drop(columns=excepts_cols, axis=1, inplace=True)
                if not model_df.columns.equals(df.columns):
                    messages.success(
                        request, "Either the columns name or columns order \
                        are not matching, Please download the format for the same.")
                    return redirect(upload_master_file)

                null_df = df.isnull().any(axis=1).sum()
                excel_file = io.BytesIO()
                if null_df != 0:
                    null_nan_mask = df.isnull() | df.isna()
                    null_nan_df = df[null_nan_mask.any(axis=1)]
                    with pd.ExcelWriter(excel_file, engine='xlsxwriter', mode='xlsx') as writer:
                        null_nan_df.to_excel(writer, index=False)
                excel_file.seek(0)
                valid_records = total_records - null_df
                invalid_records = null_df
                df = df.dropna()
                logger.info("the executing time in checking shape",
                            time.time() - global_start_time)
                task_end_time = datetime.now()
                datauploadobj = DataUploadTask( created_by=str(created_by), total_records=total_records,
                    error_records=invalid_records,
                    action=action, file_type=file_type, started_at=global_start_datetime,
                    ended_at=task_end_time,approved_by=None,approved_on=None,is_approved=None, status="Uploaded..",
                    valid_records=valid_records, file=file,
                )
                if null_df != 0:
                    datauploadobj.error_file.save('error_data.xlsx', excel_file)
                datauploadobj.save()
                logger.info("the executing time in populate the data upload task table",
                            time.time() - global_start_time)
                # latest_id=DataUploadTask.objects.latest('id').id
                # df['data_id']=latest_id
                data_json = df.to_dict(orient='records')
                save_commision_slab_rate_task.delay(data_json)
                
                messages.success(
                    request, "The data has been uploaded.")
                return redirect(upload_master_file)
        # else:
        #     logger.info('The Error in uploading form', master_form.errors)
        #     master_form = FileUploadMasterForm()

    data_upload_task_table = DataUploadTask.objects.filter(
        file_type="COMMISSION_SLAB_MASTER").order_by('-id')
    context = {
        'data_upload_task_table': data_upload_task_table,
    }
    error_message=[]
    for field, errors in master_form.errors.items():
        error_message.append(f'Errors for "{field}" field: {", ".join(errors)}')
    if error_message:
        error_message = "We have found errors in uploading the form: " + ". ".join(error_message)
        messages.error(request, error_message)
    return render(request, "home/upload_master_rate_slab.html", context)


@login_required(login_url="login")
def upload_due_blue_book(request):
    global_start_time = time.time()
    print("the time starts",global_start_time)
    global_start_datetime = datetime.now()
    form = FileIUploadForm()
    comm_sl_df = MasterRate.objects.all()
    comm_sl_df = pd.DataFrame(comm_sl_df)
    channel_partner_df = ChannelPartner.objects.all().values()
    channel_partner_df = pd.DataFrame(channel_partner_df)    
    if request.method == "POST":
        print("into the post method",time.time()-global_start_time)
        form = FileIUploadForm(request.POST, request.FILES)
        data_upload_task_table = DataUploadTask.objects.filter(
            file_type="BLUE_DUE_BOOK").order_by('-id')
        if form.is_valid():
            try:
                print("fetching the file",time.time()-global_start_time)
                file = request.FILES["file"]
                print("find the file",time.time()-global_start_time)        
            except:
                messages.success(request,"The file is not valid or corrupt. Please check file size or extention.")
            financial_year = form.cleaned_data.get("financial_year")
            action = form.cleaned_data.get("action")
            file_extension = file.name.split('.')[-1]
            if file_extension!='xlsx':
                messages.success(request,"Please upload excel file only, use extention '.xlsx'")
                return redirect(upload_due_blue_book)
            if comm_sl_df.shape[0] == 0 and channel_partner_df.shape[0] == 0:
                messages.success(request,"Data not available either in Commission Slab and Channel Partners. Please upload data to commission slab and channelpartner")
                return redirect(upload_due_blue_book)
            if channel_partner_df.shape[0] == 0:
                messages.success(request,"Data not available in channel parter, Please upload to channel partners")
                return redirect(upload_due_blue_book)
            if comm_sl_df.shape[0]==0:
                messages.success(request,"Data not available in commission slab, Please upload commission slab")
                return redirect(upload_due_blue_book)
            try:
                print("trying the excel into df",time.time()-global_start_time)
                chunksize=10000
                df = pd.read_excel(file, engine='openpyxl')
                print("conerted into df",time.time()-global_start_time)
            except Exception as e:
                messages.success(request,"The file is not valid or corrupt. Please check file size or extention.")
                return redirect(upload_due_blue_book)
            if df.shape[0]==0:
                messages.success(request,"Uploaded file have 0 records, please uplaod the correct file.")
                return redirect(upload_due_blue_book)    
            df.columns = df.columns.str.lower()
            file_type = "BLUE_DUE_BOOK"
            total_records = df.shape[0]
            created_by = str(request.user)
            if action == 'UPLOAD':
                logger.info("the executing th action time") 
                print("into the upload action",time.time()-global_start_time)
                fields = TempTable._meta.get_fields()
                fields_name = [field.name for field in fields]
                model_df = pd.DataFrame(columns=fields_name)
                excepts_cols = ['id', 'created_by', 'created_on', 'filename','financial_year',
                                'commision_amount', 'rule_name', 'collection_flag',"action"]
                model_df.drop(columns=excepts_cols, axis=1, inplace=True)                
                if not df.columns.equals(model_df.columns):
                    messages.success(
                        request, "Either the columns name or columns order are not matching, Please download the format for the same.")
                    return redirect(upload_due_blue_book)
                print("checked the columns",time.time()-global_start_time)
                fin_year = DataUploadTask.objects.filter(
                    financial_year=financial_year).count()
                if fin_year != 0:
                    messages.success(
                        request, "Data exists for the same financial year.")
                    return redirect(upload_due_blue_book)
                print("checked financial year",time.time()-global_start_time)
                null_nan_mask = df.isnull() | df.isna()
                null_nan_df = df[null_nan_mask.any(axis=1)]
                null_nan_df['error_messages']="Row has null values"
                df = df.dropna()
                print("checked null values",time.time()-global_start_time)
                def validate_and_convert_date(date):
                    try:
                        if type(date) is not int:
                            return pd.to_datetime(date, errors='coerce')
                    except (ValueError,TypeError):
                        return pd.NaT

                # Iterate through date columns and apply the function
                date_columns = ['due_month', 'actual_due_date', 'policy_effective_date', 'next_premium_due_date']
                rows_to_remove = []
                for col in date_columns:
                    df[col] = df[col].apply(validate_and_convert_date)
                    invalid_date_rows = df[df[col].isna()]
                    rows_to_remove.extend(invalid_date_rows.index)

                # Remove rows with invalid dates from the DataFrame
                rows_to_remove_df = df.loc[rows_to_remove]
                rows_to_remove_df.sort_index(inplace=True)
                rows_to_remove_df=rows_to_remove_df.drop_duplicates()
                rows_to_remove_df['error_messages']="Row have wrong date formates, please check the date columns(due_month,actual_due_date,policy_effective_date,next_premium_due_date)"
                df = df.drop(rows_to_remove_df.index)
                print("checked the date formates",time.time()-global_start_time)
                non_numeric_rows = []
                #logging.info("after check dates",df.shape)
                # List of columns to check for non-numeric values
                columns_to_check = ['annualized_target_premium', 'modal_based_premium','year_banding']

                for col in columns_to_check:
                    non_numeric_mask = pd.to_numeric(df[col], errors='coerce').isna()
                    non_numeric_rows.extend(df[non_numeric_mask].index)

                # Remove non-numeric rows from the original DataFrame
                non_numeric_df = df.loc[non_numeric_rows]
                non_numeric_df.sort_index(inplace=True)
                non_numeric_df=non_numeric_df.drop_duplicates()
                non_numeric_df['error_messages']="Row has non numeric value either in Anualised_target_premium, or Modal_based_target, or year_banding"
                df = df.drop(index=non_numeric_rows)
                print("into the upload action",time.time()-global_start_time)
                excel_file = io.BytesIO()
                if null_nan_df is not None or non_numeric_df is not None or rows_to_remove_df is not None:
                    error_df = [df for df in [null_nan_df, non_numeric_df, rows_to_remove_df] if df is not None]
                    result = pd.concat(error_df, axis=0, ignore_index=True)
                    with pd.ExcelWriter(excel_file, engine='xlsxwriter', mode='xlsx') as writer:
                        result.to_excel(writer, index=False)
                excel_file.seek(0)
                print("prepared the error file",time.time()-global_start_time)
                # Convert the columns to the appropriate data types (if needed)
                # Create a list of columns and their corresponding data types
                column_data_types = {
                    'annualized_target_premium': int,
                    'modal_based_premium': int,
                    'year_banding': int,
                    'policy_no': str,
                    'application_no': str,
                    'bank_channel_partner': str,
                    'product_name': str,
                    'product_code': str,
                    'plan_type': str,
                    'premium_frequency': str,
                    'premium_paying_term': str,
                    'policy_term': str,
                    'owner_name': str,
                    'registration_status_as_on_due_date': str,
                    'concatenate_with_merging_branch': str,
                    'rrm_name': str,
                    'zrm_name': str,
                    'cro_zh_name': str,
                    'status_of_policy': str,
                    'branch_of_sale': str,
                    'sp_agent_code': str,
                    'branch_code': str,
                    'branch_name': str,
                    'staff_non_staff': str,
                    'bank_zone': str,
                    'bank_circle': str,
                    'book_type': str
                }

                # Loop through the dictionary and apply data type conversion
                for column, data_type in column_data_types.items():
                    df[column] = df[column].astype(data_type)
                print("changed the data type of columns",time.time()-global_start_time)

                df['financial_year']=financial_year
                df['action']=action
                df['created_by']=str(request.user)
                # df['is_active']=True
                blue_df = df[df['book_type'] == "BB"]
                due_df = df[df['book_type'] == "DB"]
                print("prepared the bband db speratly",time.time()-global_start_time)
                if due_df.shape[0] != 0:
                    print("into the db and preapring the for dictionary",time.time()-global_start_time)
                    due_df = due_df.to_dict(orient="records")
                    print("into the db and preapred hte dictionary",time.time()-global_start_time)
                    model_obj = [TempTable(**row) for row in due_df]
                    print("into the db and prepared the model obj",time.time()-global_start_time)
                    try:
                        TempTable.objects.bulk_create(model_obj,batch_size= 100000)
                        print("into the db and bulk upload into the temp table",time.time()-global_start_time)
                    except Exception as e:
                        messages.success(
                            request, "Data is not correct, Please check and reupload")
                        return redirect(upload_due_blue_book)
                print("saved db temp tables.",time.time()-global_start_time)
                if blue_df.shape[0] != 0:
                    blue_df = blue_df.to_dict(orient="records")
                    model_obj = [TempTableBB(**row) for row in blue_df]
                    try:
                        TempTableBB.objects.bulk_create(model_obj,batch_size=100000)
                    except Exception as e:
                        messages.success(
                            request, "Data are not correct, Please check and reupload")
                        return redirect(upload_due_blue_book)
                print("saved into the bb temp table",time.time()-global_start_time)
                task_end_time = datetime.now()
                valid_records = df.shape[0]
                invalid_records = total_records-valid_records
                datauploadobj = DataUploadTask(
                        created_by=created_by, total_records=total_records,
                    error_records=invalid_records, financial_year=financial_year,
                    action=action, file_type=file_type, started_at=global_start_datetime,
                    ended_at=task_end_time,approved_by=None,approved_on=None,is_approved=None,
                    status="Calculating Commission",file=file,
                    valid_records=valid_records)
                if null_nan_df is not None or non_numeric_df is not None or rows_to_remove_df is not None:
                    datauploadobj.error_file.save('error_data.xlsx', excel_file)
                datauploadobj.save()
                print("saved into the data upload task",time.time()-global_start_time)
                latest_data_upload_id = DataUploadTask.objects.latest(
                    'id').id
                save_blue_due_book_task.delay(latest_data_upload_id)
                print("called the celery",time.time()-global_start_time)
                messages.success(
                    request, "The data has been uploaded and is in the progress of calculating commission")
                return redirect(upload_due_blue_book)

            elif action == "APPEND":                    
                fin_year = UploadBlueBook.objects.filter(
                    financial_year=financial_year).count()
                fin_year1 = UploadDueBook.objects.filter(
                    financial_year=financial_year).count()
                if fin_year == 0 and fin_year1 ==0:
                    messages.success(
                    request, "Data not found, please upload first then append")
                    return redirect(upload_due_blue_book)
                fields = TempTable._meta.get_fields()
                fields_name = [field.name for field in fields]
                model_df = pd.DataFrame(columns=fields_name)
                excepts_cols = ['id', 'created_by', 'created_on', 'filename','financial_year',
                                'commision_amount', 'rule_name', 'collection_flag',"action"]
                model_df.drop(columns=excepts_cols, axis=1, inplace=True)
                if not df.columns.equals(model_df.columns):
                    # print("into the not equals cols.")
                    messages.success(
                        request, "Either the columns name or columns order are not matching, Please download the format for the same.")
                    return redirect(upload_due_blue_book)
                null_nan_mask = df.isnull() | df.isna()
                null_nan_df = df[null_nan_mask.any(axis=1)]
                null_nan_df['error_messages']="Row has null values"
                df = df.dropna()

                def validate_and_convert_date(date):
                    try:
                        if type(date) is not int:
                            return pd.to_datetime(date, errors='coerce')
                    except (ValueError,TypeError):
                        return pd.NaT
                    
                date_columns = ['due_month', 'actual_due_date', 'policy_effective_date', 'next_premium_due_date']
                rows_to_remove = []
                for col in date_columns:
                    df[col] = df[col].apply(validate_and_convert_date)

                    invalid_date_rows = df[df[col].isna()]
                    rows_to_remove.extend(invalid_date_rows.index)

                # Remove rows with invalid dates from the DataFrame
                rows_to_remove_df = df.loc[rows_to_remove]
                rows_to_remove_df['error_messages']="Row have wrong date formates, please check the date columns(due_month,actual_due_date,policy_effective_date,next_premium_due_date)"
                df = df.drop(rows_to_remove_df.index)

                non_numeric_rows = []
                #logging.info("after check dates",df.shape)
                # List of columns to check for non-numeric values
                columns_to_check = ['annualized_target_premium', 'modal_based_premium','year_banding']

                for col in columns_to_check:
                    non_numeric_mask = pd.to_numeric(df[col], errors='coerce').isna()
                    non_numeric_rows.extend(df[non_numeric_mask].index)

                # Remove non-numeric rows from the original DataFrame
                non_numeric_df = df.loc[non_numeric_rows]
                non_numeric_df['error_messages']="Row has non numeric value either in Anualised_target_premium, or Modal_based_target, or year_banding"
                df = df.drop(index=non_numeric_rows)
                
                
                excel_file = io.BytesIO()
                if null_nan_df is not None or non_numeric_df is not None or rows_to_remove_df is not None:
                    error_df = [df for df in [null_nan_df, non_numeric_df, rows_to_remove_df] if df is not None]
                    result = pd.concat(error_df, axis=0, ignore_index=True)
                    with pd.ExcelWriter(excel_file, engine='xlsxwriter', mode='xlsx') as writer:
                        result.to_excel(writer, index=False)
                excel_file.seek(0)
                # Create a list of columns and their corresponding data types
                column_data_types = {
                    'annualized_target_premium': int,
                    'modal_based_premium': int,
                    'year_banding': int,
                    'policy_no': str,
                    'application_no': str,
                    'bank_channel_partner': str,
                    'product_name': str,
                    'product_code': str,
                    'plan_type': str,
                    'premium_frequency': str,
                    'premium_paying_term': str,
                    'policy_term': str,
                    'owner_name': str,
                    'registration_status_as_on_due_date': str,
                    'concatenate_with_merging_branch': str,
                    'rrm_name': str,
                    'zrm_name': str,
                    'cro_zh_name': str,
                    'status_of_policy': str,
                    'branch_of_sale': str,
                    'sp_agent_code': str,
                    'branch_code': str,
                    'branch_name': str,
                    'staff_non_staff': str,
                    'bank_zone': str,
                    'bank_circle': str,
                    'book_type': str
                }

                # Loop through the dictionary and apply data type conversion
                for column, data_type in column_data_types.items():
                    df[column] = df[column].astype(data_type)

                df['financial_year']=financial_year
                df['action']=action
                df['created_by']=str(request.user)
                upload_file=io.BytesIO()
                with pd.ExcelWriter(upload_file,engine="xlsxwriter",mode='xlsx') as writer:
                    df.to_excel(writer,index=False)
                upload_file.seek(0)
                task_end_time = datetime.now()
                valid_records = df.shape[0]
                invalid_records = total_records-valid_records
                datauploadobj = DataUploadTask(
                        created_by=created_by, total_records=total_records,
                    error_records=invalid_records, financial_year=financial_year,
                    action=action, file_type=file_type, started_at=global_start_datetime,
                    ended_at=task_end_time,approved_by=None,approved_on=None,is_approved=None,
                     status="Pending for approval",file=file,
                    valid_records=valid_records)
                if null_nan_df is not None or non_numeric_df is not None or rows_to_remove_df is not None:
                    datauploadobj.error_file.save('error_data.xlsx', excel_file)
                datauploadobj.save()
                latest_id = DataUploadTask.objects.latest('id').id
                model_obj = ApprovalData(financial_year=financial_year,
                                         data_id=latest_id,
                                         action=action, file_type=file_type,
                                         total_records=total_records,
                                         uploaded_by=str(request.user))
                if df.shape[0]!=0:
                    model_obj.file.save("approval_data.xlsx",upload_file)
                model_obj.save()
                
               # Query the "approver" group
                group = Group.objects.get(name='approver')

                # Get the users in the group
                users_in_group = group.user_set.all()

                # Email configuration
                from_email = 'noreply.automationhub@canarahsbclife.in'
                backend = EmailBackend(
                    host='smtp.netcorecloud.net',
                    port='587',
                    username='rpa1',
                    password='Canara@12345',
                    use_tls=True,
                    fail_silently=False
                )

                # Loop through the users and send an email to each one
                for user in users_in_group:
                    user_email = user.email
                    created_on = datetime.now().date()
                    email_subject = 'Records submitted for approval'
                    email_body = f"Records have been uploaded for approval at agent commission system\nThe Details are given below:\nUploaded By: {request.user}\nTotal Records: {total_records}\nCreated On: {created_on}"

                    msg = EmailMessage(
                        subject=email_subject,
                        body=email_body,
                        from_email=f'Support Automation Hub <{from_email}>',
                        to=[user_email],
                        connection=backend
                    )
                    msg.send(fail_silently=False)
                messages.success(
                    request, "For the selected Action, you need approval, Please ask approver to approve.")
                return redirect(upload_due_blue_book)
            elif action == "REPLACE":
                fin_year = UploadBlueBook.objects.filter(
                    financial_year=financial_year).count()
                fin_year1 = UploadDueBook.objects.filter(
                    financial_year=financial_year).count()
                if fin_year == 0 and fin_year1 == 0:
                    messages.success(
                    request, "Data not found, please upload first then replace")
                    return redirect(upload_due_blue_book)
                fields = TempTable._meta.get_fields()
                fields_name = [field.name for field in fields]
                model_df = pd.DataFrame(columns=fields_name)
                excepts_cols = ['id', 'created_by', 'created_on', 'filename','financial_year',
                                'commision_amount', 'rule_name', 'collection_flag',"action"]
                model_df.drop(columns=excepts_cols, axis=1, inplace=True)
                if not df.columns.equals(model_df.columns):
                    # print("into the not equals cols.")
                    messages.success(
                        request, "Either the columns name or columns order are not matching, Please download the format for the same.")
                    return redirect(upload_due_blue_book)
                null_nan_mask = df.isnull() | df.isna()
                null_nan_df = df[null_nan_mask.any(axis=1)]
                null_nan_df['error_messages']="Row has null values"
                df = df.dropna()

                def validate_and_convert_date(date):
                    try:
                        return pd.to_datetime(date, errors='coerce')
                    except ValueError:
                        return pd.NaT
                    
                date_columns = ['due_month', 'actual_due_date', 'policy_effective_date', 'next_premium_due_date']
                rows_to_remove = []
                for col in date_columns:
                    df[col] = df[col].apply(validate_and_convert_date)
                    invalid_date_rows = df[df[col].isna()]
                    rows_to_remove.extend(invalid_date_rows.index)

                # Remove rows with invalid dates from the DataFrame
                df = df.drop(index=rows_to_remove)
                rows_to_remove_df = df.loc[rows_to_remove]
                rows_to_remove_df['error_messages']="Row have wrong date formates, please check the date columns(due_month,actual_due_date,policy_effective_date,next_premium_due_date)"
                # df = df.drop(rows_to_remove_df.index)
                df = df.drop(rows_to_remove_df.index)

                non_numeric_rows = []
                #logging.info("after check dates",df.shape)
                # List of columns to check for non-numeric values
                columns_to_check = ['annualized_target_premium', 'modal_based_premium','year_banding']

                for col in columns_to_check:
                    non_numeric_mask = pd.to_numeric(df[col], errors='coerce').isna()
                    non_numeric_rows.extend(df[non_numeric_mask].index)

                # Remove non-numeric rows from the original DataFrame
                non_numeric_df = df.loc[non_numeric_rows]
                non_numeric_df['error_messages']="Row has non numeric value either in Anualised_target_premium, or Modal_based_target, or year_banding"
                df = df.drop(index=non_numeric_rows)
                
                
                excel_file = io.BytesIO()
                if null_nan_df is not None or non_numeric_df is not None or rows_to_remove_df is not None:
                #logging.info("into the error loop")
                    error_df = [df for df in [null_nan_df, non_numeric_df, rows_to_remove_df] if df is not None]
                    # Concatenate DataFrames along columns (side by side)
                    result = pd.concat(error_df, axis=0, ignore_index=True)
                    # Export the concatenated DataFrame to an Excel file
                    with pd.ExcelWriter(excel_file, engine='xlsxwriter', mode='xlsx') as writer:
                        result.to_excel(writer, index=False)
                    # data_json_error = null_nan_df.to_dict(orient="records")
                    # save_error_table.delay(data_json_error)

                excel_file.seek(0)
                df['annualized_target_premium'] = df['annualized_target_premium'].astype(int)
                df['modal_based_premium'] = df['modal_based_premium'].astype(int)
                df['year_banding'] = df['year_banding'].astype(int)            
                df['policy_no']=df['policy_no'].astype(str)
                df['application_no']=df['application_no'].astype(str)
                df['bank_channel_partner']=df['bank_channel_partner'].astype(str)
                df['product_name']=df['product_name'].astype(str)
                df['product_code']=df['product_code'].astype(str)
                df['plan_type']=df['plan_type'].astype(str)
                df['premium_frequency']=df['premium_frequency'].astype(str)
                df['premium_paying_term']=df['premium_paying_term'].astype(str)
                df['policy_term']=df['policy_term'].astype(str)
                df['owner_name']=df['owner_name'].astype(str)
                df['registration_status_as_on_due_date']=df['registration_status_as_on_due_date'].astype(str)
                df['concatenate_with_merging_branch']=df['concatenate_with_merging_branch'].astype(str)
                df['rrm_name']=df['rrm_name'].astype(str)
                df['zrm_name']=df['zrm_name'].astype(str)
                df['cro_zh_name']=df['cro_zh_name'].astype(str)
                df['status_of_policy']=df['status_of_policy'].astype(str)
                df['branch_of_sale']=df['branch_of_sale'].astype(str)
                df['sp_agent_code']=df['sp_agent_code'].astype(str)
                df['branch_code']=df['branch_code'].astype(str)
                df['branch_name']=df['branch_name'].astype(str)
                df['staff_non_staff']=df['staff_non_staff'].astype(str)
                df['bank_zone']=df['bank_zone'].astype(str)
                df['bank_circle']=df['bank_circle'].astype(str)
                df['book_type']=df['book_type'].astype(str)
                df['financial_year']=financial_year
                df['action']=action
                df['created_by']=str(request.user)
                upload_file=io.BytesIO()
                with pd.ExcelWriter(upload_file,engine="xlsxwriter",mode='xlsx') as writer:
                    df.to_excel(writer,index=False)
                upload_file.seek(0)
                task_end_time = datetime.now()
                valid_records = df.shape[0]
                invalid_records = total_records-valid_records
                datauploadobj = DataUploadTask(
                        created_by=created_by, total_records=total_records,
                    error_records=invalid_records, financial_year=financial_year,
                    action=action, file_type=file_type, started_at=global_start_datetime,
                    ended_at=task_end_time,approved_by=None,approved_on=None,is_approved=None,
                    status="Pending for approval",file=file,
                    valid_records=valid_records)
                if null_nan_df is not None or non_numeric_df is not None or rows_to_remove_df is not None:
                    datauploadobj.error_file.save('error_data.xlsx', excel_file)
                datauploadobj.save()
                latest_id = DataUploadTask.objects.latest('id').id
                model_obj = ApprovalData(financial_year=financial_year,
                                         data_id=latest_id,
                                         action=action, file_type=file_type,
                                         total_records=total_records,
                                         uploaded_by=str(request.user))
                if df.shape[0]!=0:
                    model_obj.file.save("approval_data.xlsx",upload_file)
                model_obj.save()
                messages.success(
                    request, "For the selected Action, you need approval, Please ask approver to approve.")
                return redirect(upload_due_blue_book)  
            
    data_upload_task_table = DataUploadTask.objects.filter(
        file_type="BLUE_DUE_BOOK").order_by('-id')
    context = {
        'data_upload_task_table': data_upload_task_table
    }
    error_message=[]
    for field, errors in form.errors.items():
        error_message.append(f'Errors for "{field}" field: {", ".join(errors)}')
    if error_message:
        error_message = "We have found errors in uploading the form: " + ". ".join(error_message)
        messages.error(request, error_message)
    return render(request, "home/upload_due_blue_book.html", context)

@login_required(login_url="login")
def upload_collection_flag(request):
    global_start_time = time.time()
    global_start_datetime = datetime.now()
    collection_form=FileUploadCollectionFlagForm()
    if request.method == "POST":
        collection_form = FileUploadCollectionFlagForm(
            request.POST, request.FILES)
        data_upload_task_table = DataUploadTask.objects.filter(
            file_type="COLLECTION_FLAG").order_by('-id')
        bb=UploadBlueBook.objects.all()
        db=UploadDueBook.objects.all()
        if bb is None and not db.exists():
            messages.success(request,"There are no records in BB or DB, Please upload some records first.")
            return redirect(upload_collection_flag)
        if collection_form.is_valid():
            file = request.FILES['file']
            # df = pd.read_excel(file)
            file_extension = file.name.split('.')[-1]
            if file_extension!='xlsx':
                messages.success(request,"Please upload excel file only, use extention '.xlsx'")
                return redirect(upload_collection_flag)
            df = pd.read_excel(file, engine='openpyxl')
            total_records = df.shape[0]
            df.columns = df.columns.str.lower()
            null_nan_mask = df.isnull() | df.isna()
            null_nan_df = df[null_nan_mask.any(axis=1)]
            null_nan_df['error_messages']="Row has null values"
            df = df.dropna()
            df['counter']=pd.to_numeric(df['counter'],errors="coerce")
            non_counter=df[df['counter']<=0]            
            non_counter['error_messages']="Row has counter value 0 or less."
            df=df[~(df['counter']<=0)]
            df['collection_flag']=df['collection_flag'].astype(str)
            non_y=df[~(df['collection_flag']=="Y")]
            non_y['error_messages']="Row has no 'Y' value in collection flag column."
            df=df[df['collection_flag']=="Y"]
            excel_file = io.BytesIO()
            if null_nan_df is not None or non_counter is not None or non_y is not None:
            #logging.info("into the error loop")
                error_df = [df for df in [null_nan_df, non_counter, non_y] if df is not None]
                # Concatenate DataFrames along columns (side by side)
                result = pd.concat(error_df, axis=0, ignore_index=True)
                # Export the concatenated DataFrame to an Excel file
                with pd.ExcelWriter(excel_file, engine='xlsxwriter', mode='xlsx') as writer:
                    result.to_excel(writer, index=False)

            excel_file.seek(0)

            logger.info("the executing time in checking shape")
            task_end_time = datetime.now()
            valid_records = df.shape[0]
            invalid_records = total_records-valid_records
            datauploadobj = DataUploadTask(
                 created_by=str(request.user), total_records=total_records,
                error_records=invalid_records, file_type="COLLECTION_FLAG", started_at=global_start_datetime,
                ended_at=task_end_time, status="Uploaded..",action="UPLOAD",file=file,
                valid_records=valid_records,is_approved=None,approved_on=None,approved_by=None
            )
            if null_nan_df is not None or non_counter is not None or non_y is not None:
                datauploadobj.error_file.save('collection_flag_error_data.xlsx', excel_file)
            datauploadobj.save()
            latest_data_upload_id = DataUploadTask.objects.latest(
                    'id').id
            model_obj = [CollectionUpdate(**row)
                         for row in df.to_dict(orient='records')]
            CollectionUpdate.objects.bulk_create(model_obj)
            update_collection_flag.delay(latest_data_upload_id)            
            messages.success(
                request, "The collection flags has been uploaded.")
            return redirect(upload_collection_flag)

    data_upload_task_table = DataUploadTask.objects.filter(
        file_type="COLLECTION_FLAG").order_by('-id')
    context = {
        'data_upload_task_table': data_upload_task_table,
    }
    error_message=[]
    for field, errors in collection_form.errors.items():
        error_message.append(f'Errors for "{field}" field: {", ".join(errors)}')
    if error_message:
        error_message = "We have found errors in uploading the form: " + ". ".join(error_message)
        messages.error(request, error_message)
    return render(request, 'home/upload_collection_flag.html',context)

class MasterVIewLIstView(UserPassesTestMixin, ListView):
    model = MasterRate
    template_name = "home/master_view_reports.html"
    context_object_name = 'model_obj'
    paginate_by = 10
    @method_decorator(login_required(login_url=reverse_lazy('login')))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    def get_queryset(self):
        queryset=MasterRate.objects.all()
        self.product_name=self.request.GET.get('product_name')
        self.product_code=self.request.GET.get('product_code')
        self.is_staff=self.request.GET.get('is_staff')
        self.rule_name=self.request.GET.get('rule_name')
        self.year_from=self.request.GET.get('year_from')
        self.pt_from=self.request.GET.get('pt_from')
        self.ppt_from=self.request.GET.get('ppt_from')
        self.premium_from=self.request.GET.get('premium_from')
        self.ape_from=self.request.GET.get('ape_from')
        self.rate=self.request.GET.get('rate')
        if self.product_name:
            queryset = queryset.filter(product_name__istartswith=self.product_name)
        if self.product_code:
            queryset = queryset.filter(product_code__istartswith=self.product_code)
        if self.is_staff:
            queryset = queryset.filter(is_staff__istartswith=self.is_staff)
        if self.rule_name:
            queryset = queryset.filter(rule_name__istartswith=self.rule_name)
        if self.year_from:
            queryset = queryset.filter(year_from__gte=self.year_from)
        if self.pt_from:
            queryset = queryset.filter(pt_from__gte=self.pt_from)
        if self.ppt_from:
            queryset = queryset.filter(ppt_from__gte=self.ppt_from)
        if self.premium_from:
            queryset = queryset.filter(premium_from__gte=self.premium_from)
        if self.ape_from:
            queryset = queryset.filter(ape_from__gte=self.ape_from)
        if self.rate:
            queryset = queryset.filter(rate__gte=self.rate)
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = self.get_queryset()
        paginator = Paginator(items, self.paginate_by)
        page_number = self.request.GET.get('page')
        page = paginator.get_page(page_number)
        context['page'] = page
        # Create a dictionary of filter parameters for dynamic pagination links
        filter_params = {
            'product_name': self.product_name,
            'product_code': self.product_code,
            'is_staff': self.is_staff,
            'rule_name': self.rule_name,
            'year_from': self.year_from,
            'pt_from': self.pt_from,
            'ppt_from': self.ppt_from,
            'premium_from': self.premium_from,
            'ape_from': self.ape_from,
            'rate': self.rate,
        }
        context['filter_params'] = filter_params
        context['total_records'] = items.count()
        self.request.session['filter_params'] = filter_params
        return context
    def test_func(self):
        return user_has_permission(self.request.user, 'chsbc_hub.view_masterrate')
    def handle_no_permission(self):
        error_message = "You don't have permission to access this page."
        return render(
            self.request,
            '403_forbidden.html',
            {'error_message': error_message},
            status=403
        )

def stream_commission_slab_view_data(request):
    filter_params = request.session.get('filter_params', {})
    # Retrieve filtered data based on filter_params
    queryset = MasterRate.objects.all()
    # Apply filters based on filter_params
    for field, value in filter_params.items():
        if value:
            queryset = queryset.filter(**{field + '__istartswith': value})

    # Convert queryset to a DataFrame
    included_fields  = ["product_name",  "product_code","year_from",    "year_to",
    "pt_from",
    "pt_to",
    "ppt_from",
    "ppt_to",
    "premium_from",
    "premium_to",
    "ape_from",
    "ape_to",
    "is_staff",
    "rule_name",
    "rate",
]
    data = list(queryset.values(*included_fields))
    df = pd.DataFrame(data)

    # Create an Excel file in memory
    excel_file = io.BytesIO()
    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)

    # Set the file pointer to the beginning of the file
    excel_file.seek(0)

    # Create an HTTP response for file download
    response = HttpResponse(
        excel_file.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = 'attachment; filename="filtered_data.xlsx"'

    return response

class BlueDueListView(UserPassesTestMixin, ListView):
    # model = UploadDueBook
    template_name = "home/due_blue_book_view_report.html"
    context_object_name = "model_obj"
    paginate_by = 10
    @method_decorator(login_required(login_url=reverse_lazy('login')))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    def get_queryset(self):
        queryset1 = UploadDueBook.objects.all()
        queryset2 = UploadBlueBook.objects.all()
        
        filters = {}
        # Populate the filters dictionary with values from the request
        for key, value in self.request.GET.items():
            if key != 'page' and value:  # Exclude 'page' parameter from filters
                filters[key + '__istartswith'] = value
        # Apply the filters to the queryset using Q objects
        q_objects = Q()
        for field, value in filters.items():
            q_objects &= Q(**{field: value  })
        queryset1 = queryset1.filter(q_objects)

        # filters = {}
        # Populate the filters dictionary with values from the request
        for key, value in self.request.GET.items():
            if key != 'page' and value:  # Exclude 'page' parameter from filters
                filters[key + '__istartswith'] = value
        # Apply the filters to the queryset using Q objects
        q_objects = Q()
        for field, value in filters.items():
            q_objects &= Q(**{field: value  })
        queryset2 = queryset2.filter(q_objects)

        queryset= list(queryset1) + list(queryset2)
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = self.get_queryset()
        paginator = Paginator(items, self.paginate_by)
        page_number = self.request.GET.get('page')
        page = paginator.get_page(page_number)
        # Get the current filter parameters
        filter_params = {key: value for key, value in self.request.GET.items() if value}
        # Add filter parameters to the pagination links
        page_links = []
        for i in page.paginator.page_range:
            page_links.append({
                'page_number': i,
                'url': f"?{urlencode({**filter_params, 'page': i})}",
            })
        context['page'] = page
        context['filter_params'] = filter_params
        context['page_links'] = page_links
        context['total_records'] = len(items)
        commission_amount_total = sum(item.commision_amount for item in items)
        
        # context['commission_amount_total'] = locale.format_string("%.2f", commission_amount_total,grouping=False)
        context['commission_amount_total'] = format_decimal(commission_amount_total, locale='en_IN', decimal_quantization=1)
        self.request.session['filter_params'] = filter_params
        return context
    def test_func(self):
        return user_has_permission(self.request.user, 'chsbc_hub.view_uploadbluebook')

    def handle_no_permission(self):
        error_message = "You don't have permission to access this page."
        return render(
            self.request,
            '403_forbidden.html',
            {'error_message': error_message},
            status=403
        )

def stream_bb_db_view_data(request):
    filter_params = request.session.get('filter_params',{})
    queryset1=UploadBlueBook.objects.all()
    queryset2=UploadDueBook.objects.all()
    for field,value in filter_params.items():
        if value:
            queryset1 = queryset1.filter(**{field + '__istartswith': value})
            queryset2 = queryset2.filter(**{field + '__istartswith': value})
    included_fields = [
    "policy_no",
    "application_no",
    "bank_channel_partner",
    "product_name",
    "product_code",
    "plan_type",
    "premium_frequency",
    "premium_paying_term",
    "policy_term",
    "annualized_target_premium",
    "modal_based_premium",
    "due_month",
    "actual_due_date",
    "policy_effective_date",
    "year_banding",
    "next_premium_due_date",
    "owner_name",
    "registration_status_as_on_due_date",
    "concatenate_with_merging_branch",
    "rrm_name",
    "zrm_name",
    "cro_zh_name",
    "status_of_policy",
    "branch_of_sale",
    "sp_agent_code",
    "commision_amount",
    "branch_code",
    "branch_name",
    "staff_non_staff",
    "bank_zone",
    "bank_circle",
    # "filename",
    "collection_flag",
    "book_type",
    "rule_name",
    "is_match_with_channel_partners",
    "created_on",
    "financial_year",]

    data = list(queryset1.values(*included_fields)) + list(queryset2.values(*included_fields))
    df = pd.DataFrame(data)
    df['created_on'] = pd.to_datetime(df['created_on']).dt.strftime('%Y-%m-%d %H:%M:%S')
    print("---"*100,type(df['created_on']))
    print("---"*100,(df['created_on']))
    excel_file = io.BytesIO()
    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        df.to_excel(writer,index=False)
    excel_file.seek(0)
    response = HttpResponse(
        excel_file.read(),
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = 'attachment; filename="filtered_data.xlsx"'

    return response

class ChannelPartnerListView(UserPassesTestMixin, ListView):

    model = ChannelPartner
    template_name = "home/channel_partner_view.html"
    context_object_name = "model_objs"
    paginate_by = 10

    @method_decorator(login_required(login_url=reverse_lazy('login')))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    def get_queryset(self):
        queryset = ChannelPartner.objects.all()
        self.plan_code = self.request.GET.get('plan_code')
        self.channel_code = self.request.GET.get('channel_code')
        self.concatenate = self.request.GET.get('concatenate')
        self.rule_name = self.request.GET.get('rule_name')

        if self.plan_code:
            queryset = queryset.filter(plan_code__icontains=self.plan_code)
        if self.channel_code:
            queryset = queryset.filter(channel_code__icontains=self.channel_code)
        if self.concatenate:
            queryset = queryset.filter(concatenate__icontains=self.concatenate)
        if self.rule_name:
            queryset = queryset.filter(rule_name__icontains=self.rule_name)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = self.get_queryset()
        paginator = Paginator(items, self.paginate_by)
        page_number = self.request.GET.get('page')
        page = paginator.get_page(page_number)
        context['page'] = page
        # Create a dictionary of filter parameters for dynamic pagination links
        filter_params = {
            'plan_code': self.plan_code,
            'channel_code': self.channel_code,
            'concatenate': self.concatenate,
            'rule_name': self.rule_name,
        }
        context['total_records'] = len(items)
        context['filter_params'] = filter_params
        return context

    def test_func(self):
        return user_has_permission(self.request.user, 'chsbc_hub.view_channelpartner')

    def handle_no_permission(self):
        error_message = "You don't have permission to access this page."
        return render(
            self.request,
            '403_forbidden.html',
            {'error_message': error_message},
            status=403
        )
