# def task_id_d(request):
#     try:
#         print("into the task")
#         go_to_sleep.delay(2)
#     except Exception as e:
#         print("the error in celery ",e)
#     # time.sleep(5)
#     return render(request,"home/master_celery.html")

# @shared_task
# def my_task(self, seconds):
#     progress_recorder = ProgressRecorder(self)
#     result = 0
#     for i in range(seconds):
#         time.sleep(1)
#         result += 2
#         progress_recorder.set_progress(i + 1, seconds)
#     return result   


# def do_work(list_work):
#     for work_item in list_work:
#         work_item
#     return "work is complete"


# def save_master_data(data):
#     print("into the master slab data save")
#     # print("the data",data)
#     # print("the type ",type(data))
#     for index,rows in data.iterrows():
#         # print(item)
#         # print("into the master slab form")
#         form = MasterRateForm(rows)
#         print(form)
#         print("trying to save master form")
#         if form.is_valid():
#             # print("master form has been saved")
#             form.save()
#             print("the data has been save to master slab data")
#         else:
#             print("the error in saving the data")









# {% extends "base.html" %}
# {% block title %} merchant-engagement {% endblock %}

# {% block content %}
# <style>
#   .loader {
#       border: 4px solid rgb(0, 191, 255);
#       border-top: 4px solid #3498db;
#       border-radius: 50%;
#       width: 40px;
#       height: 40px;
#       animation: spin 2s linear infinite;
#       margin: 0 auto;
#       margin-top: 20px;
#   }

#   @keyframes spin {
#       0% { transform: rotate(0deg); }
#       100% { transform: rotate(360deg); }
#   }
# </style>
# <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
# <a href="#" class="btn btn-secondary">Back</a>
# </div>


# {% include 'includes/sidebar.html' %}
# {% include 'includes/navigation.html' %}

# <div class="container mt-4">
#     <div class="row justify-content-around mt-5 mb-2">
#         <div class="col-md-2">
#             <a href="#" class="btn btn-secondary"><i class="bi bi-arrow-return-left"></i> Back</a>
#         </div>
#         <div class="col-md-7"></div>
#     </div>
#     {% comment %} file upload section {% endcomment %}
#     <div class="row justify-content-center">

#         <!-- master data form starts here -->
#         <div class="col-md-6">
#             <div class="card">
#                 <div class="card-header">
#                     <h1 class="text-center" >Upload Master Rate Slab</h1>
#                 </div>
#                     <div class="card-body">
#                         {% if not master_form.submitted %}
#                         <form method="post" class="form" action="{% url 'upload_master_file' %}" enctype="multipart/form-data">
#                             {% csrf_token %}

#                             <a href="{% url 'download_csv' %}" download>Download Excel format for master data</a><br><br>
#                             <div class="form-group">
#                                 {{master_form.as_p}}
#                             </div>
#                                 <button type="submit"  onclick="showLoader(); performServerProcessing();" class="btn btn-primary">Submit</button>
#                         </form>
#                         {% endif %}
#                         {% comment %} <div class='progress-wrapper'>
#                             <div id='progress-bar' class='progress-bar' style="background-color: #68a9ef; width: 0%;">&nbsp;</div>
#                           </div>
#                         <div id="progress-bar-message">Waiting for progress to start...</div>             {% endcomment %}

#                         <div id="progress-message"></div>
#     <div class="progress">
#         <div id="progress-bar" class="progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
#     </div>
#                         {% if master_form.submitted %}
#                           {{http_response.content}}
#                         {% endif %}
#                         {% if master_form.errors %}
#                         <ul class="errorlist">
#                             {% for field in master_form %}
#                                 {% for error in field.errors %}
#                                     <li>{{ error }}</li>
#                                 {% endfor %}
#                             {% endfor %}
#                         </ul>
#                         {% endif %}
#                     </div>
#             </div>
#         </div>
#     </div>
# </div>

# <script>
#   function showLoader() {
#       document.getElementById("loader").style.display = "block";
#   }

#   function hideLoader() {
#       document.getElementById("loader").style.display = "none";
#   }
# </script>

# <script>
#     function performServerProcessing() {
#         // Simulate server processing (you would typically make an AJAX request here)
#         setTimeout(function () {
#             // Once processing is complete, hide the loader
#             hideLoader();
#         }, 3000); // Simulating a 3-second processing time
#     }
# </script>
# <script>

# // vanilla JS version
# {% comment %} document.addEventListener("DOMContentLoaded", function () {
#     var progressUrl = "{% url 'celery_progress:task_status' 2 %}";
#     CeleryProgressBar.initProgressBar(progressUrl);
#   }); {% endcomment %}

# function updateProgress(progressBarElement, progressBarMessageElement, progress) {
#   progressBarElement.style.width = progress.percent + "%";
#   progressBarMessageElement.innerHTML = progress.current + ' of ' + progress.total + ' processed.';
# }

# var trigger = document.getElementById('progress-bar-trigger');
# trigger.addEventListener('click', function(e) {
#   var bar = document.getElementById("progress-bar");
#   var barMessage = document.getElementById("progress-bar-message");
#   for (var i = 0; i < 11; i++) {
#     setTimeout(updateProgress, 500 * i, bar, barMessage, {
#       percent: 10 * i,
#       current: 10 * i,
#       total: 100
#     })
#   }
# })
# </script>

# {% endblock content %}


            # columns_mapping={
            #     'Product Name':'product_name',
            #     'Product Code': 'product_code',
            #     'Staff/Non_Staff':'is_staff',
            #     'Rule Name':'rule_name'
            # }
            # df.rename(columns=columns_mapping,inplace=True)
            # df.columns = df.columns.str.lower()
            


            

            # logger.info(error_records_df.shape)
            # logger.info(error_records_df.head())
            # error_records_df=BytesIO()
            
            # with pd.ExcelWriter(error_records_df, engine='openpyxl') as writer:
            #     df.to_excel(writer,index=False,sheet_name='error sheet')
            
            # # error_records_df.seek(0)
            # # excel_records_data=error_records_df.read()
            # # excel_records_data_base64=base64.b64encode(excel_records_data).decode()
            # logger.info("the executing time in bulk create",time.time()-global_start_time)









# def data_upload_task(filename,total_records,error_records,financial_year,
#                      operation_action,file_type,created_by):
#     obj=DataUploadTask(filename=filename,total_records=total_records,
#                        error_records=error_records,financial_year=financial_year,
#                        action=operation_action,file_type=file_type,
#                        created_by=created_by)
#     obj.save()

# def approval_process(request):
#     #there will a screen for the same.
#     pass





# def process_excel_file(file):
#     df = pd.read_excel(file)
#     df.columns = df.columns.str.lower()
#     df.rate = df.rate.fillna(3)
#     total_records=df.shape[0]
#     # data = df.to_dict(orient="records")
#     return df,total_records


# def save_blue_due_book(data):
#     for item in data:
#         form = TempTableForm(item)
#         if form.is_valid():
#             form.save()
#         else:
#             pass


# def save_error_data(data):
#     for item in data:
#         form = ErrorTableForm(item)
#         if form.is_valid():
#             form.save()
#         else:
#             pass


# DB configuration
# from sqlalchemy import create_engine
# DB_NAME= os.getenv('POSTGRES_DB')
# DB_USER= os.getenv('POSTGRES_USER')
# DB_PASSWORD= os.getenv('POSTGRES_PASSWORD')
# DB_HOST= os.getenv('POSTGRES_HOST')
# DB_PORT= os.getenv('POSTGRES_PORT')
# db_url=f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
# engine=create_engine(db_url)
# conn=engine.connect()


    #         # populate table according to acton and file_type
    #         if action == "UPLOAD_NEW":
    #             df,total_records= process_excel_file(file)

    #             if df.isnull().any():
    #                 null_values= df[df.isnull().any(axis=1)]
    #                 save_error_data(null_values)
    #             else:
    #                 not_null_values = df[~df.isnull().any(axis=1)]
    #                 save_blue_due_book(not_null_values)

    #         elif action == "APPEND_IN_BLUE_DUE_RECORDS":
    #             # create a obj from temp blue book and check if any common col
    #             # use pd.merge for common cols
    #             obj = UploadBlueBook()
    #             df_bb = ""
    #             df = process_excel_file(file)
    #             if df["book_type"] == "BB":
    #                 obj = UploadBlueBook()
    #                 pass
    #             elif df["book_type"] == "DB":
    #                 pass
    #             pass
    #         elif (
    #             action == "UPDATE_IN_BLUE_DUE_RECORDS" and file_type == "DUE_BLUE_BOOK"
    #         ):
    #             pass
    #         elif (
    #             action == "REPLACE_IN_BLUE_DUE_RECORDS" and file_type == "DUE_BLUE_BOOK"
    #         ):
    #             pass

    #         elif file_type == "DUE_BLUE_BOOK":
    #             df = process_excel_file(file)
    #             if df.isnull().any():
    #                 null_values = df[df.isnull().any(axis=1)]
    #                 form = ErrorTableForm(null_values)
    #                 if form.is_valid():
    #                     form.save()

    #             else:
    #                 obj = UploadDueBook.objects.filter(financial_year=financial_year)
    #                 if obj is not None:
    #                     pass
    #                 save_blue_due_book(df)

    #         logger.info(financial_year, action, file_type)
    #         logger.info("form saved--")
    #         return render(request, "home/upload_due_blue_book.html")
    #     else:
    #         logger.info("not found the file--")
    # else:
    #     form = FileIUploadForm()
    #     master_form = FileUploadMasterForm()
    #     return render(
    #         request,
    #         "home/upload_due_blue_book.html",
    #         {"master_form": master_form, "form": form},
    #     )
    # return render(request, "home/upload_due_blue_book.html")
