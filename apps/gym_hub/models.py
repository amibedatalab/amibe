from django.contrib.auth.models import Permission
from django.utils.translation import gettext as _
from fileinput import filename
from logging import Manager
from platform import mac_ver
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models
User = get_user_model()
from datetime import datetime

class FileUpload(models.Model):
    file = models.FileField(upload_to='uploads/chsbc/')
    financial_year = models.CharField(_("Financial Year"),
                                      max_length=10, null=True)
    operation_action = models.CharField(_("Operation/Action"),
                                        max_length=50, null=True)
    file_type = models.CharField(_("File Type"), max_length=20, null=True)


class DataUploadTask(models.Model):

    created_by = models.CharField(_("Created By"), max_length=50,
                                  null=True, blank=True)
    created_on = models.DateTimeField(
        _('Created On'), auto_now_add=True, null=True)
    total_records = models.IntegerField(null=True)
    valid_records = models.IntegerField(null=True)
    error_records = models.IntegerField(null=True)
    financial_year = models.CharField(_("Financial Year"), max_length=20,)
    action = models.CharField(_("Action"), max_length=50, null=True)
    file_type = models.CharField(max_length=50, null=True)
    status = models.CharField(
        _('Status'), max_length=150, blank=True, null=True, default="Completed..")
    error_message = models.CharField(
        _("Error message"), max_length=50, default="No Error...")
    started_at = models.DateTimeField(
        _("Task Started At"), auto_now=False, auto_now_add=False, null=True)
    ended_at = models.DateTimeField(
        _("Task Ended At"), auto_now=False, auto_now_add=False, null=True)
    approved_by = models.CharField(
        _("Approved By"), max_length=50, null=True, blank=True)
    approved_on = models.DateTimeField(
        _("Approved On"), auto_now_add=False, null=True, blank=True)
    is_approved = models.BooleanField(
        _("Is Approved"), null=True, blank=True, default=True)
    def file_upload_path(instance, filename):
        # Define the dynamic upload path based on the file_type, created_by, and current timestamp
        if instance.file_type == "COMMISSION_SLAB_MASTER":
            return f"Commission_slab/File/{instance.created_by}/{datetime.timestamp(datetime.now())}/{filename}"
        elif instance.file_type == "BLUE_DUE_BOOK":
            return f"Blue_book/File/{instance.created_by}/{datetime.timestamp(datetime.now())}/{filename}"
        elif instance.file_type == "COLLECTION_FLAG":
            return f"Collection/File/{instance.created_by}/{datetime.timestamp(datetime.now())}/{filename}"
        else:
            raise ValueError("Invalid file_type")

    def error_file_upload_path(instance, filename):
        # Define the dynamic error file upload path based on the file_type, created_by, and current timestamp
        if instance.file_type == "MASTER_RATE":
            return f"Commission_slab/Error/{instance.created_by}/{datetime.timestamp(datetime.now())}/{filename}"
        elif instance.file_type == "BLUE_DUE_BOOK":
            return f"Blue_book/Error/{instance.created_by}/{datetime.timestamp(datetime.now())}/{filename}"
        elif instance.file_type == "COLLECTION_FLAG":
            return f"Collection/Error/{instance.created_by}/{datetime.timestamp(datetime.now())}/{filename}"
        else:
            raise ValueError("Invalid file_type")
    file = models.FileField(_("File"), upload_to=file_upload_path,null=True)
    error_file = models.FileField(_("Error File"), upload_to=error_file_upload_path,null=True)

    class Meta:
        managed = True
        db_table = "data_upload_task"
        verbose_name = "Data Upload Task"
        verbose_name_plural = "Data Upload Task"

    def __str__(self):
        return str(self.file_type)


class CollectionUpdate(models.Model):
    policy_no = models.CharField(_("Policy No."), max_length=50,
                                 null=True, blank=True)
    collection_flag = models.CharField(_("Collection Flag"),max_length=5,
                                          default="No", null=True, blank=True)
    counter = models.IntegerField(_("Counter"), null=True, blank=True)

    class Meta:
        managed = True
        db_table = "collection_update"
        verbose_name = "Collection Update"
        verbose_name_plural = "Collection Update"

    def __str__(self):
        return str(self.policy_no)
    
class TempTableCollectionUpdate(models.Model):
    policy_no = models.CharField(_("Policy No."), max_length=50,
                                 null=True, blank=True)
    collection_flag = models.CharField(_("Collection Flag"),max_length=5,
                                          default="No", null=True, blank=True)
    counter = models.IntegerField(_("Counter"), null=True, blank=True)

    class Meta:
        managed = True
        db_table = "temp_collection_update"
        verbose_name = "temp_Collection Update"
        verbose_name_plural = "temp_Collection Update"

    def __str__(self):
        return str(self.policy_no)    


class TempTable(models.Model):

    policy_no = models.CharField(_("Policy No."),
                                 max_length=50, null=True, blank=True)
    application_no = models.CharField(_("Application No."),
                                      max_length=50, null=True, blank=True)
    bank_channel_partner = models.CharField(_("Bank/Channel Partner Name"),
                                            max_length=200, null=True, blank=True)
    product_name = models.CharField(_("Product Name"),
                                    max_length=200, null=True, blank=True)
    product_code = models.CharField(_("Product Code"),
                                    max_length=50, null=True, blank=True)
    plan_type = models.CharField(_("Plan Type"),
                                 max_length=100, null=True, blank=True)
    premium_frequency = models.CharField(_("Premium Frequency"),
                                         max_length=50, null=True, blank=True)
    premium_paying_term = models.CharField(_("PPT(Premium Paying Term)"),
                                           max_length=50, null=True, blank=True)
    policy_term = models.CharField(_("Policy Term"),
                                   max_length=50, null=True, blank=True)
    annualized_target_premium = models.IntegerField(_
                                                    ("Annualised Target Premium"), null=True, blank=True)
    modal_based_premium = models.IntegerField(
        _("Modal Based Premium"), null=True, blank=True)
    due_month = models.DateField(_("Due Month"),
                                       auto_now=False, auto_now_add=False, null=True, blank=True)
    actual_due_date = models.DateField(_("Actual Due Date"),
                                       auto_now=False, auto_now_add=False, null=True, blank=True)
    policy_effective_date = models.DateField(_("Policy Effective Date"),
                                             auto_now=False, auto_now_add=False, null=True, blank=True)
    year_banding = models.IntegerField(_("Yr Banding"), null=True, blank=True)
    next_premium_due_date = models.DateField(_("Next Premium Due Date"),
                                             auto_now=False, auto_now_add=False, null=True, blank=True)
    owner_name = models.CharField(_("Owner Name"),
                                  max_length=50, null=True, blank=True)
    registration_status_as_on_due_date = models.CharField(_(
        "Registration Status as on due date"), max_length=50, null=True,
        blank=True)
    concatenate_with_merging_branch = models.CharField(_
                                                       ("Concatenate with merging branch"), max_length=50, null=True, blank=True)
    rrm_name = models.CharField(_("RRM name"),
                                max_length=50, null=True, blank=True)
    zrm_name = models.CharField(_("ZRM name"),
                                max_length=50, null=True, blank=True)
    cro_zh_name = models.CharField(_("CRO ZH name"),
                                   max_length=50, null=True, blank=True)
    status_of_policy = models.CharField(_("Status of Policy"),
                                        max_length=100, null=True, blank=True)
    branch_of_sale = models.CharField(_("Branch of Sale"),
                                      max_length=100, null=True, blank=True)
    sp_agent_code = models.CharField(_("SP/Agent Code"),
                                     max_length=100, null=True, blank=True)
    commision_amount = models.FloatField(_("Commission Amount"), default=0)
    branch_code = models.CharField(_("Branch Code"),
                                   max_length=50, null=True, blank=True)
    branch_name = models.CharField(_("Branch Name"),
                                   max_length=100, null=True, blank=True)
    staff_non_staff = models.CharField(_("Staff/Non Staff"),
                                       max_length=100, null=True, blank=True)
    bank_zone = models.CharField(_("Bank Zone"),
                                 max_length=100, null=True, blank=True)
    bank_circle = models.CharField(_("Bank Circle"),
                                   max_length=50, null=True, blank=True)
    filename = models.CharField(_("Filename"),
                                max_length=100, blank=True, null=True)
    collection_flag = models.CharField(_("Collection Flag"), max_length=20,
                                       default="N", null=True, blank=True)
    created_by = models.CharField(_("Created By"),
                                  max_length=50, null=True, blank=True)
    created_on = models.DateTimeField(_("Uploaded On"),
                                      auto_now_add=True)
    book_type = models.CharField(_("Book Type"), max_length=20,
                                 null=True, blank=True)
    rule_name = models.CharField(
        _("Rule Name"), null=True, blank=True, max_length=5)
    action = models.CharField(_("Action"), max_length=50, null=True)
    financial_year = models.CharField(_("Financial Year"), max_length=20,null=True)

    class Meta:
        managed = True
        db_table = "temp_table_db"
        verbose_name = "Temp_Table_DB"
        verbose_name_plural = "Temp_Table_DB"

    def __str__(self):
        return str(self.policy_no)

class TempTableBB(models.Model):

    policy_no = models.CharField(_("Policy No."),
                                 max_length=50, null=True, blank=True)
    application_no = models.CharField(_("Application No."),
                                      max_length=50, null=True, blank=True)
    bank_channel_partner = models.CharField(_("Bank/Channel Partner Name"),
                                            max_length=200, null=True, blank=True)
    product_name = models.CharField(_("Product Name"),
                                    max_length=200, null=True, blank=True)
    product_code = models.CharField(_("Product Code"),
                                    max_length=50, null=True, blank=True)
    plan_type = models.CharField(_("Plan Type"),
                                 max_length=100, null=True, blank=True)
    premium_frequency = models.CharField(_("Premium Frequency"),
                                         max_length=50, null=True, blank=True)
    premium_paying_term = models.CharField(_("PPT(Premium Paying Term)"),
                                           max_length=50, null=True, blank=True)
    policy_term = models.CharField(_("Policy Term"),
                                   max_length=50, null=True, blank=True)
    annualized_target_premium = models.IntegerField(_
                                                    ("Annualised Target Premium"), null=True, blank=True)
    modal_based_premium = models.IntegerField(
                                 null=True, blank=True)
    due_month = models.DateField(_("Due Month"),
                                       auto_now=False, auto_now_add=False, null=True, blank=True)
    actual_due_date = models.DateField(_("Actual Due Date"),
                                       auto_now=False, auto_now_add=False, null=True, blank=True)
    policy_effective_date = models.DateField(_("Policy Effective Date"),
                                             auto_now=False, auto_now_add=False, null=True, blank=True)
    year_banding = models.IntegerField(_("Yr Banding"), null=True, blank=True)
    next_premium_due_date = models.DateField(_("Next Premium Due Date"),
                                             auto_now=False, auto_now_add=False, null=True, blank=True)
    owner_name = models.CharField(_("Owner Name"),
                                  max_length=50, null=True, blank=True)
    registration_status_as_on_due_date = models.CharField(_(
        "Registration Status as on due date"), max_length=50, null=True,
        blank=True)
    concatenate_with_merging_branch = models.CharField(_
                                                       ("Concatenate with merging branch"), max_length=50, null=True, blank=True)
    rrm_name = models.CharField(_("RRM name"),
                                max_length=50, null=True, blank=True)
    zrm_name = models.CharField(_("ZRM name"),
                                max_length=50, null=True, blank=True)
    cro_zh_name = models.CharField(_("CRO ZH name"),
                                   max_length=50, null=True, blank=True)
    status_of_policy = models.CharField(_("Status of Policy"),
                                        max_length=100, null=True, blank=True)
    branch_of_sale = models.CharField(_("Branch of Sale"),
                                      max_length=100, null=True, blank=True)
    sp_agent_code = models.CharField(_("SP/Agent Code"),
                                     max_length=100, null=True, blank=True)
    commision_amount = models.FloatField(_("Commission Amount"), default=0)
    branch_code = models.CharField(_("Branch Code"),
                                   max_length=50, null=True, blank=True)
    branch_name = models.CharField(_("Branch Name"),
                                   max_length=100, null=True, blank=True)
    staff_non_staff = models.CharField(_("Staff/Non Staff"),
                                       max_length=100, null=True, blank=True)
    bank_zone = models.CharField(_("Bank Zone"),
                                 max_length=100, null=True, blank=True)
    bank_circle = models.CharField(_("Bank Circle"),
                                   max_length=50, null=True, blank=True)
    filename = models.CharField(_("Filename"),
                                max_length=100, blank=True, null=True)
    collection_flag = models.CharField(_("Collection Flag"), max_length=20,
                                       default="N", null=True, blank=True)
    created_by = models.CharField(_("Created By"),
                                  max_length=50, null=True, blank=True)
    created_on = models.DateTimeField(_("Uploaded On"),
                                      auto_now_add=True)
    book_type = models.CharField(_("Book Type"), max_length=20,
                                 null=True, blank=True)
    rule_name = models.CharField(
        _("Rule Name"), null=True, blank=True, max_length=5)
    action = models.CharField(_("Action"), max_length=50, null=True)
    financial_year = models.CharField(_("Financial Year"), max_length=20,null=True)

    class Meta:
        managed = True
        db_table = "temp_table_bb"
        verbose_name = "Temp_Table_BB"
        verbose_name_plural = "Temp_Table_BB"

    def __str__(self):
        return str(self.policy_no)


class ErrorTable(models.Model):

    policy_no = models.CharField(_("Policy No."),
                                 max_length=50, null=True, blank=True)
    application_no = models.CharField(_("Application No."),
                                      max_length=50, null=True, blank=True)
    bank_channel_partner = models.CharField(_("Bank/Channel Partner Name"),
                                            max_length=200, null=True, blank=True)
    product_name = models.CharField(_("Product Name"),
                                    max_length=200, null=True, blank=True)
    product_code = models.CharField(_("Product Code"),
                                    max_length=50, null=True, blank=True)
    plan_type = models.CharField(_("Plan Type"),
                                 max_length=100, null=True, blank=True)
    premium_frequency = models.CharField(_("Premium Frequency"),
                                         max_length=50, null=True, blank=True)
    premium_paying_term = models.CharField(_("PPT(Premium Paying Term)"),
                                           max_length=50, null=True, blank=True)
    policy_term = models.CharField(_("Policy Term"),
                                   max_length=50, null=True, blank=True)
    annualized_target_premium = models.IntegerField(_
                                                    ("Annualised Target Premium"), null=True, blank=True)
    modal_based_premium = models.IntegerField(
        _("Modal Based Premium"), null=True, blank=True)
    due_month = models.DateField(_("Due Month"),
                                       auto_now=False, auto_now_add=False, null=True, blank=True)
    actual_due_date = models.DateField(_("Actual Due Date"),
                                       auto_now=False, auto_now_add=False, null=True, blank=True)
    policy_effective_date = models.DateField(_("Policy Effective Date"),
                                             auto_now=False, auto_now_add=False, null=True, blank=True)
    year_banding = models.IntegerField(_("Yr Banding"), null=True, blank=True)
    next_premium_due_date = models.DateField(_("Next Premium Due Date"),
                                             auto_now=False, auto_now_add=False, null=True, blank=True)
    owner_name = models.CharField(_("Owner Name"),
                                  max_length=50, null=True, blank=True)
    registration_status_as_on_due_date = models.CharField(_(
        "Registration Status as on due date"), max_length=50, null=True,
        blank=True)
    concatenate_with_merging_branch = models.CharField(_
                                                       ("Concatenate with merging branch"), max_length=50, null=True, blank=True)
    rrm_name = models.CharField(_("RRM name"),
                                max_length=50, null=True, blank=True)
    zrm_name = models.CharField(_("ZRM name"),
                                max_length=50, null=True, blank=True)
    cro_zh_name = models.CharField(_("CRO ZH name"),
                                   max_length=50, null=True, blank=True)
    status_of_policy = models.CharField(_("Status of Policy"),
                                        max_length=100, null=True, blank=True)
    branch_of_sale = models.CharField(_("Branch of Sale"),
                                      max_length=100, null=True, blank=True)
    sp_agent_code = models.CharField(_("SP/Agent Code"),
                                     max_length=100, null=True, blank=True)
    commision_amount = models.FloatField(_("Commission Amount"), default=0)
    branch_code = models.CharField(_("Branch Code"),
                                   max_length=50, null=True, blank=True)
    branch_name = models.CharField(_("Branch Name"),
                                   max_length=100, null=True, blank=True)
    staff_non_staff = models.CharField(_("Staff/Non Staff"),
                                       max_length=100, null=True, blank=True)
    bank_zone = models.CharField(_("Bank Zone"),
                                 max_length=100, null=True, blank=True)
    bank_circle = models.CharField(_("Bank Circle"),
                                   max_length=50, null=True, blank=True)
    filename = models.CharField(_("Filename"),
                                max_length=100, blank=True, null=True)
    collection_flag = models.CharField(_("Collection Flag"), max_length=20,
                                       default="N", null=True, blank=True)
    created_by = models.CharField(_("Created By"),
                                  max_length=50, null=True, blank=True)
    created_on = models.DateTimeField(_("Uploaded On"),
                                      auto_now_add=True)
    book_type = models.CharField(_("Book Type"), max_length=20,
                                 null=True, blank=True)
    rule_name = models.CharField(
        _("Rule Name"), null=True, blank=True, max_length=5)
    action = models.CharField(_("Action"), max_length=50, null=True)
    class Meta:
        managed = True
        db_table = "error_table_bb_db"
        verbose_name = "Temp_Table_BB_DB"
        verbose_name_plural = "Temp_Table_BB_DB"

    def __str__(self):
        return str(self.policy_no)


class UploadDueBook(models.Model):

    policy_no = models.CharField(_("Policy No."),
                                 max_length=50, null=True, blank=True)
    application_no = models.CharField(_("Application No."),
                                      max_length=50, null=True, blank=True)
    bank_channel_partner = models.CharField(_("Bank/Channel Partner Name"),
                                            max_length=200, null=True, blank=True)
    product_name = models.CharField(_("Product Name"),
                                    max_length=200, null=True, blank=True)
    product_code = models.CharField(_("Product Code"),
                                    max_length=50, null=True, blank=True)
    plan_type = models.CharField(_("Plan Type"),
                                 max_length=100, null=True, blank=True)
    premium_frequency = models.CharField(_("Premium Frequency"),
                                         max_length=50, null=True, blank=True)
    premium_paying_term = models.CharField(_("PPT(Premium Paying Term)"),
                                           max_length=50, null=True, blank=True)
    policy_term = models.CharField(_("Policy Term"),
                                   max_length=50, null=True, blank=True)
    annualized_target_premium = models.IntegerField(_
                                                    ("Annualised Target Premium"), null=True, blank=True)
    modal_based_premium = models.IntegerField(
        _("Modal Based Premium"), null=True, blank=True)
    due_month = models.DateField(_("Due Month"),
                                       auto_now=False, auto_now_add=False, null=True, blank=True)
    actual_due_date = models.DateField(_("Actual Due Date"),
                                       auto_now=False, auto_now_add=False, null=True, blank=True)
    policy_effective_date = models.DateField(_("Policy Effective Date"),
                                             auto_now=False, auto_now_add=False, null=True, blank=True)
    year_banding = models.IntegerField(_("Yr Banding"), null=True, blank=True)
    next_premium_due_date = models.DateField(_("Next Premium Due Date"),
                                             auto_now=False, auto_now_add=False, null=True, blank=True)
    owner_name = models.CharField(_("Owner Name"),
                                  max_length=50, null=True, blank=True)
    registration_status_as_on_due_date = models.CharField(_(
        "Registration Status as on due date"), max_length=50, null=True,
        blank=True)
    concatenate_with_merging_branch = models.CharField(_
                                                       ("Concatenate with merging branch"), max_length=50, null=True, blank=True)
    rrm_name = models.CharField(_("RRM name"),
                                max_length=50, null=True, blank=True)
    zrm_name = models.CharField(_("ZRM name"),
                                max_length=50, null=True, blank=True)
    cro_zh_name = models.CharField(_("CRO ZH name"),
                                   max_length=50, null=True, blank=True)
    status_of_policy = models.CharField(_("Status of Policy"),
                                        max_length=100, null=True, blank=True)
    branch_of_sale = models.CharField(_("Branch of Sale"),
                                      max_length=100, null=True, blank=True)
    sp_agent_code = models.CharField(_("SP/Agent Code"),
                                     max_length=100, null=True, blank=True)
    commision_amount = models.FloatField(_("Commission Amount"), default=0)
    branch_code = models.CharField(_("Branch Code"),
                                   max_length=50, null=True, blank=True)
    branch_name = models.CharField(_("Branch Name"),
                                   max_length=100, null=True, blank=True)
    staff_non_staff = models.CharField(_("Staff/Non Staff"),
                                       max_length=100, null=True, blank=True)
    bank_zone = models.CharField(_("Bank Zone"),
                                 max_length=100, null=True, blank=True)
    bank_circle = models.CharField(_("Bank Circle"),
                                   max_length=50, null=True, blank=True)
    filename = models.CharField(_("Filename"),
                                max_length=100, blank=True, null=True)
    collection_flag = models.CharField(_("Collection Flag"), max_length=20,
                                       default="N", null=True, blank=True)
    book_type = models.CharField(_("Book Type"), max_length=20,
                                 null=True, blank=True)
    rule_name = models.CharField(
        _("Rule Name"), null=True, blank=True, max_length=5)
    is_match_with_commission_slab=models.CharField(_("Is match with commission slab"), max_length=100,
                                                    null=True, blank=True)
    is_match_with_channel_partners=models.CharField(_("Is match with channel partners"), max_length=100,
                                                    null=True, blank=True)
    action = models.CharField(_("Action"), max_length=50, null=True)
    financial_year = models.CharField(_("Financial Year"), max_length=20,null=True)
    created_by = models.CharField(
        _("Created By"), max_length=50, null=True, blank=True)
    created_on = models.DateTimeField(_("Uploaded On"), auto_now_add=False)
    modified_on = models.DateTimeField(_("Modified On"), auto_now=True)
    modified_by = models.CharField(
        _("Modified By"), max_length=50, null=True, blank=True)
    approved_by = models.CharField(
        _("Approved By"), max_length=50, null=True, blank=True)
    approved_on = models.DateTimeField(
        _("Approved On"), auto_now=False, auto_now_add=False, null=True, blank=True)
    is_approved = models.BooleanField(_("Is Approved"), null=True, blank=True)

    class Meta:
        managed = True
        db_table = "processed_due_book"
        verbose_name = "Processed Due Book"
        verbose_name_plural = "Processed Due Book"

    def __str__(self):
        return str(self.policy_no)


class UploadBlueBook(models.Model):

    policy_no = models.CharField(_("Policy No."),
                                 max_length=50, null=True, blank=True)
    application_no = models.CharField(_("Application No."),
                                      max_length=50, null=True, blank=True)
    bank_channel_partner = models.CharField(_("Bank/Channel Partner Name"),
                                            max_length=200, null=True, blank=True)
    product_name = models.CharField(_("Product Name"),
                                    max_length=200, null=True, blank=True)
    product_code = models.CharField(_("Product Code"),
                                    max_length=50, null=True, blank=True)
    plan_type = models.CharField(_("Plan Type"),
                                 max_length=100, null=True, blank=True)
    premium_frequency = models.CharField(_("Premium Frequency"),
                                         max_length=50, null=True, blank=True)
    premium_paying_term = models.CharField(_("PPT(Premium Paying Term)"),
                                           max_length=50, null=True, blank=True)
    policy_term = models.CharField(_("Policy Term"),
                                   max_length=50, null=True, blank=True)
    annualized_target_premium = models.IntegerField(_
                                                    ("Annualised Target Premium"), null=True, blank=True)
    modal_based_premium = models.IntegerField(
        _("Modal Based Premium"), null=True, blank=True)
    due_month = models.DateField(_("Due Month"),
                                       auto_now=False, auto_now_add=False, null=True, blank=True)
    actual_due_date = models.DateField(_("Actual Due Date"),
                                       auto_now=False, auto_now_add=False, null=True, blank=True)
    policy_effective_date = models.DateField(_("Policy Effective Date"),
                                             auto_now=False, auto_now_add=False, null=True, blank=True)
    year_banding = models.IntegerField(_("Yr Banding"), null=True, blank=True)
    next_premium_due_date = models.DateField(_("Next Premium Due Date"),
                                             auto_now=False, auto_now_add=False, null=True, blank=True)
    owner_name = models.CharField(_("Owner Name"),
                                  max_length=50, null=True, blank=True)
    registration_status_as_on_due_date = models.CharField(_(
        "Registration Status as on due date"), max_length=50, null=True,
        blank=True)
    concatenate_with_merging_branch = models.CharField(_
                                                       ("Concatenate with merging branch"), max_length=50, null=True, blank=True)
    rrm_name = models.CharField(_("RRM name"),
                                max_length=50, null=True, blank=True)
    zrm_name = models.CharField(_("ZRM name"),
                                max_length=50, null=True, blank=True)
    cro_zh_name = models.CharField(_("CRO ZH name"),
                                   max_length=50, null=True, blank=True)
    status_of_policy = models.CharField(_("Status of Policy"),
                                        max_length=100, null=True, blank=True)
    branch_of_sale = models.CharField(_("Branch of Sale"),
                                      max_length=100, null=True, blank=True)
    sp_agent_code = models.CharField(_("SP/Agent Code"),
                                     max_length=100, null=True, blank=True)
    commision_amount = models.FloatField(_("Commission Amount"), default=0)
    branch_code = models.CharField(_("Branch Code"),
                                   max_length=50, null=True, blank=True)
    branch_name = models.CharField(_("Branch Name"),
                                   max_length=100, null=True, blank=True)
    staff_non_staff = models.CharField(_("Staff/Non Staff"),
                                       max_length=100, null=True, blank=True)
    bank_zone = models.CharField(_("Bank Zone"),
                                 max_length=100, null=True, blank=True)
    bank_circle = models.CharField(_("Bank Circle"),
                                   max_length=50, null=True, blank=True)
    filename = models.CharField(_("Filename"),
                                max_length=100, blank=True, null=True)
    collection_flag = models.CharField(_("Collection Flag"), max_length=20,
                                       default="N", null=True, blank=True)
    is_match_with_commission_slab=models.CharField(_("Is match with commission slab"), max_length=100,
                                                    null=True, blank=True)
    is_match_with_channel_partners=models.CharField(_("Is match with channel partners"), max_length=100,
                                                    null=True, blank=True)
    book_type = models.CharField(_("Book Type"), max_length=20,
                                 null=True, blank=True)
    rule_name = models.CharField(
        _("Rule Name"), null=True, blank=True, max_length=5)
    action = models.CharField(_("Action"), max_length=50, null=True)
    financial_year = models.CharField(_("Financial Year"), max_length=20,null=True)
    created_by = models.CharField(
        _("Created By"), max_length=50, null=True, blank=True)
    created_on = models.DateTimeField(_("Uploaded On"), auto_now_add=False)
    modified_on = models.DateTimeField(_("Modified On"), auto_now=True)
    modified_by = models.CharField(
        _("Modified By"), max_length=50, null=True, blank=True)
    approved_by = models.CharField(
        _("Approved By"), max_length=50, null=True, blank=True)
    approved_on = models.DateTimeField(
        _("Approved On"), auto_now=False, auto_now_add=False, null=True, blank=True)
    is_approved = models.BooleanField(_("Is Approved"), null=True, blank=True)

    class Meta:
        managed = True
        db_table = "processed_blue_book"
        verbose_name = "Processed Blue Book"
        verbose_name_plural = "Processed Blue Book"

    def __str__(self):
        return str(self.policy_no)


class MasterRate(models.Model):
    data_id = models.BigIntegerField(_("Data Upload ID"), null=True)
    product_name = models.CharField(
        _("Product Name"), max_length=100, null=True, blank=True)
    product_code = models.CharField(
        _("Product Code"), max_length=100, null=True, blank=True)
    year_from = models.IntegerField(_("Year from"), null=True, blank=True)
    year_to = models.IntegerField(_("Year to"), null=True, blank=True)
    pt_from = models.IntegerField(_("PT from"), null=True, blank=True)
    pt_to = models.IntegerField(_("PT to"), null=True, blank=True)
    ppt_from = models.IntegerField(_("PPT from"), null=True, blank=True)
    ppt_to = models.IntegerField(_("PPT to"), null=True, blank=True)
    premium_from = models.IntegerField(
        _("Premium from"), null=True, blank=True)
    premium_to = models.BigIntegerField(_("Premium to"), null=True, blank=True)
    ape_from = models.IntegerField(_("APE from"), null=True, blank=True)
    ape_to = models.IntegerField(_("APE to"), null=True, blank=True)
    is_staff = models.CharField(
        _("Is Staff"), null=True, blank=True, max_length=50)
    rule_name = models.CharField(
        _("Rule Name"), null=True, blank=True, max_length=5)
    rate = models.DecimalField(
        _("Rate"), null=True, blank=True, max_digits=30, decimal_places=2, default=3)
    action = models.CharField(_("Action"), max_length=50, null=True)
    created_by = models.CharField(
        _("Created By"), max_length=50, null=True, blank=True)
    created_on = models.DateTimeField(_("Uploaded On"), auto_now_add=True)
    modified_on = models.DateTimeField(_("Modified On"), auto_now=True)
    modified_by = models.CharField(
        _("Modified By"), max_length=50, null=True, blank=True)
    approved_by = models.CharField(
        _("Approved By"), max_length=50, null=True, blank=True)
    approved_on = models.DateTimeField(
        _("Approved On"), auto_now=False, auto_now_add=False, null=True, blank=True)
    is_approved = models.BooleanField(_("Is Approved"), null=True, blank=True)
    is_active = models.BooleanField(_("Is Active"),default=True)

    class Meta:
        managed = True
        db_table = "commission_slab"
        verbose_name = "Commission Slab"
        verbose_name_plural = "Commission Slab"

    def __str__(self):
        return str(self.product_name)


# Audit trail tables---

class AU_MasterRate(models.Model):
    id = models.BigIntegerField(primary_key=True)
    revision_id = models.BigIntegerField(unique=True)
    product_name = models.CharField(
        _("Product Name"), max_length=50, null=True, blank=True)
    product_code = models.CharField(
        _("Product Code"), max_length=50, null=True, blank=True)
    year_from = models.IntegerField(_("Year from"), null=True, blank=True)
    year_to = models.IntegerField(_("Year to"), null=True, blank=True)
    pt_from = models.IntegerField(_("PT from"), null=True, blank=True)
    pt_to = models.IntegerField(_("PT to"), null=True, blank=True)
    ppt_to = models.IntegerField(_("PPT to"), null=True, blank=True)
    ppt_from = models.IntegerField(_("PPT from"), null=True, blank=True)
    premium_from = models.IntegerField(
        _("Premium from"), null=True, blank=True)
    premium_to = models.IntegerField(_("Premium to"), null=True, blank=True)
    ape_from = models.IntegerField(_("APE from"), null=True, blank=True)
    ape_to = models.IntegerField(_("APE to"), null=True, blank=True)
    is_staff = models.BooleanField(_("Is Staff"), null=True, blank=True)
    rule_name = models.CharField(
        _("Rule Name"), null=True, blank=True, max_length=5)
    rate = models.FloatField(_("Rate"), null=True, blank=True)
    action = models.CharField(_("Action"), max_length=50, null=True)
    created_by = models.CharField(
        _("Created By"), max_length=50, null=True, blank=True)
    created_on = models.DateTimeField(_("Uploaded On"), auto_now_add=True)
    modified_on = models.DateTimeField(_("Modified On"), auto_now=True)
    modified_by = models.CharField(
        _("Modified By"), max_length=50, null=True, blank=True)
    approved_by = models.CharField(
        _("Approved By"), max_length=50, null=True, blank=True)
    approved_on = models.DateTimeField(
        _("Approved On"), auto_now=False, auto_now_add=False, null=True, blank=True)
    is_approved = models.BooleanField(_("Is Approved"), null=True, blank=True)

    class Meta:
        managed = True
        db_table = "au_commission_slab"
        verbose_name = "AU Commission Slab"
        verbose_name_plural = "AU Commission Slab"

    def __str__(self):
        return str(self.product_name)


class AU_UploadeDueBook(models.Model):
    id = models.BigIntegerField(primary_key=True)
    revision_id = models.BigIntegerField(unique=True)
    policy_no = models.CharField(
        _("Policy No."), max_length=50, null=True, blank=True)
    application_no = models.CharField(
        _("Application No."), max_length=50, null=True, blank=True)
    bank_channel_partner = models.CharField(
        _("Bank/Channel Partner Name"), max_length=50, null=True, blank=True)
    product_name = models.CharField(
        _("Product Name"), max_length=50, null=True, blank=True)
    product_code = models.CharField(
        _("Product Code"), max_length=50, null=True, blank=True)
    plan_type = models.CharField(
        _("Plan Type"), max_length=50, null=True, blank=True)
    premium_frequency = models.CharField(
        _("Premium Frequency"), max_length=50, null=True, blank=True)
    premium_paying_term = models.CharField(
        _("PPT(Premium Paying Term)"), max_length=50, null=True, blank=True)
    policy_term = models.CharField(
        _("Policy Term"), max_length=50, null=True, blank=True)
    annualized_target_premium = models.IntegerField(
        _("Annualised Target Premium"), null=True, blank=True)
    modal_based_premium = models.IntegerField(
        _("Modal Based Premium"), null=True, blank=True)
    due_month = models.DateField(_("Due Month"),
                                       auto_now=False, auto_now_add=False, null=True, blank=True)
    actual_due_date = models.DateField(
        _("Actual Due Date"), auto_now=False, auto_now_add=False, null=True, blank=True)
    policy_effective_date = models.DateField(
        _("Policy Effective Date"), auto_now=False, auto_now_add=False, null=True, blank=True)
    year_banding = models.IntegerField(_("Yr Banding"), null=True, blank=True)
    next_premium_due_date = models.DateField(
        _("Next Premium Due Date"), auto_now=False, auto_now_add=False, null=True, blank=True)
    owner_name = models.CharField(
        _("Owner Name"), max_length=50, null=True, blank=True)
    registration_status_as_on_due_date = models.CharField(
        _("Registration Status as on due date"), max_length=50, null=True, blank=True)
    concatenate_with_merging_branch = models.CharField(
        _("Concatenate with merging branch"), max_length=50, null=True, blank=True)
    rrm_name = models.CharField(
        _("RRM name"), max_length=50, null=True, blank=True)
    zrm_name = models.CharField(
        _("ZRM name"), max_length=50, null=True, blank=True)
    cro_zh_name = models.CharField(
        _("CRO ZH name"), max_length=50, null=True, blank=True)
    status_of_policy = models.CharField(
        _("Status of Policy"), max_length=50, null=True, blank=True)
    branch_of_sale = models.CharField(
        _("Branch of Sale"), max_length=50, null=True, blank=True)
    sp_agent_code = models.CharField(
        _("SP/Agent Code"), max_length=50, null=True, blank=True)
    commision_amount = models.FloatField(
        _("Commission Amount"), null=True, blank=True)
    branch_code = models.CharField(
        _("Branch Code"), max_length=50, null=True, blank=True)
    branch_name = models.CharField(
        _("Branch Name"), max_length=50, null=True, blank=True)
    staff_non_staff = models.CharField(
        _("Staff/Non Staff"), max_length=50, null=True, blank=True)
    bank_zone = models.CharField(
        _("Bank Zone"), max_length=50, null=True, blank=True)
    bank_circle = models.CharField(
        _("Bank Circle"), max_length=50, null=True, blank=True)
    filename = models.CharField(
        _("Filename"), max_length=100, blank=True, null=True)
    collection_flag = models.CharField(_("Collection Flag"), max_length=20,
                                       default="N", null=True, blank=True)
    book_type = models.CharField(_("Book Type"), max_length=20,
                                 null=True, blank=True)
    rule_name = models.CharField(
        _("Rule Name"), null=True, blank=True, max_length=5)
    action = models.CharField(_("Action"), max_length=50, null=True)
    created_by = models.CharField(
        _("Created By"), max_length=50, null=True, blank=True)
    created_on = models.DateTimeField(_("Uploaded On"), auto_now_add=True)
    modified_on = models.DateTimeField(_("Modified On"), auto_now=True)
    modified_by = models.CharField(
        _("Modified By"), max_length=50, null=True, blank=True)
    approved_by = models.CharField(
        _("Approved By"), max_length=50, null=True, blank=True)
    approved_on = models.DateTimeField(
        _("Approved On"), auto_now=False, auto_now_add=False, null=True, blank=True)
    is_approved = models.BooleanField(_("Is Approved"), null=True, blank=True)

    class Meta:
        managed = True
        db_table = "au_processed_due_book"
        verbose_name = "AU Processed Due Book"
        verbose_name_plural = "AU Processed Due Book"

    def __str__(self):
        return str(self.product_name)


class AU_UploadeBlueBook(models.Model):
    id = models.BigIntegerField(primary_key=True)
    revision_id = models.BigIntegerField(unique=True)
    policy_no = models.CharField(
        _("Policy No."), max_length=50, null=True, blank=True)
    application_no = models.CharField(
        _("Application No."), max_length=50, null=True, blank=True)
    bank_channel_partner = models.CharField(
        _("Bank/Channel Partner Name"), max_length=50, null=True, blank=True)
    product_name = models.CharField(
        _("Product Name"), max_length=50, null=True, blank=True)
    product_code = models.CharField(
        _("Product Code"), max_length=50, null=True, blank=True)
    plan_type = models.CharField(
        _("Plan Type"), max_length=50, null=True, blank=True)
    premium_frequency = models.CharField(
        _("Premium Frequency"), max_length=50, null=True, blank=True)
    premium_paying_term = models.CharField(
        _("PPT(Premium Paying Term)"), max_length=50, null=True, blank=True)
    policy_term = models.CharField(
        _("Policy Term"), max_length=50, null=True, blank=True)
    annualized_target_premium = models.IntegerField(
        _("Annualised Target Premium"), null=True, blank=True)
    modal_based_premium = models.IntegerField(
        _("Modal Based Premium"), null=True, blank=True)
    due_month = models.DateField(_("Due Month"),
                                       auto_now=False, auto_now_add=False, null=True, blank=True)
    actual_due_date = models.DateField(
        _("Actual Due Date"), auto_now=False, auto_now_add=False, null=True, blank=True)
    policy_effective_date = models.DateField(
        _("Policy Effective Date"), auto_now=False, auto_now_add=False, null=True, blank=True)
    year_banding = models.IntegerField(_("Yr Banding"), null=True, blank=True)
    next_premium_due_date = models.DateField(
        _("Next Premium Due Date"), auto_now=False, auto_now_add=False, null=True, blank=True)
    owner_name = models.CharField(
        _("Owner Name"), max_length=50, null=True, blank=True)
    registration_status_as_on_due_date = models.CharField(
        _("Registration Status as on due date"), max_length=50, null=True, blank=True)
    concatenate_with_merging_branch = models.CharField(
        _("Concatenate with merging branch"), max_length=50, null=True, blank=True)
    rrm_name = models.CharField(
        _("RRM name"), max_length=50, null=True, blank=True)
    zrm_name = models.CharField(
        _("ZRM name"), max_length=50, null=True, blank=True)
    cro_zh_name = models.CharField(
        _("CRO ZH name"), max_length=50, null=True, blank=True)
    status_of_policy = models.CharField(
        _("Status of Policy"), max_length=50, null=True, blank=True)
    branch_of_sale = models.CharField(
        _("Branch of Sale"), max_length=50, null=True, blank=True)
    sp_agent_code = models.CharField(
        _("SP/Agent Code"), max_length=50, null=True, blank=True)
    commision_amount = models.FloatField(
        _("Commission Amount"), null=True, blank=True)
    branch_code = models.CharField(
        _("Branch Code"), max_length=50, null=True, blank=True)
    branch_name = models.CharField(
        _("Branch Name"), max_length=50, null=True, blank=True)
    staff_non_staff = models.CharField(
        _("Staff/Non Staff"), max_length=50, null=True, blank=True)
    bank_zone = models.CharField(
        _("Bank Zone"), max_length=50, null=True, blank=True)
    bank_circle = models.CharField(
        _("Bank Circle"), max_length=50, null=True, blank=True)
    filename = models.CharField(
        _("Filename"), max_length=100, blank=True, null=True)
    collection_flag = models.CharField(_("Collection Flag"), max_length=20,
                                       default="N", null=True, blank=True)
    book_type = models.CharField(_("Book Type"), max_length=20,
                                 null=True, blank=True)
    rule_name = models.CharField(
        _("Rule Name"), null=True, blank=True, max_length=5)
    action = models.CharField(_("Action"), max_length=50, null=True)
    created_by = models.CharField(
        _("Created By"), max_length=50, null=True, blank=True)
    created_on = models.DateTimeField(_("Uploaded On"), auto_now_add=True)
    modified_on = models.DateTimeField(_("Modified On"), auto_now=True)
    modified_by = models.CharField(
        _("Modified By"), max_length=50, null=True, blank=True)
    approved_by = models.CharField(
        _("Approved By"), max_length=50, null=True, blank=True)
    approved_on = models.DateTimeField(
        _("Approved On"), auto_now=False, auto_now_add=False, null=True, blank=True)
    is_approved = models.BooleanField(_("Is Approved"), null=True, blank=True)

    class Meta:
        managed = True
        db_table = "au_processed_blue_book"
        verbose_name = "AU Processed Blue Book"
        verbose_name_plural = "AU Processed Blue Book"

    def __str__(self):
        return str(self.product_name)


class ChannelPartner(models.Model):
    plan_code = models.CharField(max_length=80, null=False, blank=False)
    channel_code = models.CharField(max_length=80, null=False, blank=False)
    concatenate = models.CharField(max_length=80, null=False, blank=False)
    rule_name = models.CharField(max_length=80, null=False, blank=False)
    is_active = models.BooleanField(_("Is Active"),default=True,null=True)
    class Meta:
        managed = True
        db_table = "channel_partner"
        verbose_name = "Channel Partner"
        verbose_name_plural = "Channel Partner"


class ApproverPermission(Permission):
    class Meta:
        verbose_name = 'Approver'
        verbose_name_plural = 'Custom Approve Permission'


class ApprovalData(models.Model):
    data_id = models.BigIntegerField(null=True)
    financial_year = models.CharField(_("Financial Year"), max_length=20,)
    total_records = models.IntegerField(null=True)
    file_type = models.CharField(max_length=50, null=True)
    action = models.CharField(_("Action"), max_length=50, null=True)
    is_approved = models.BooleanField(
        _("Is Approved"), null=True, blank=True, default=None)
    uploaded_by = models.CharField(_("Created By"), max_length=50,
                                   null=True, blank=True)
    file = models.FileField(
        _("File"), upload_to="uploads/", max_length=100, null=True)
    message = models.CharField(_("Rejection Message"), max_length=100)
    approved_on = models.DateTimeField(
        _("Approved On"), auto_now_add=False, null=True, blank=True)
    approved_by = models.CharField(
        _("Approved By"), max_length=50, null=True, blank=True)

    class Meta:
        db_table = "approval_data"
        verbose_name = "Approval Data"
        verbose_name_plural = "Approval Data"


class AU_ApprovalData(models.Model):

    revision_id = models.BigIntegerField(unique=True)
    financial_year = models.CharField(_("Financial Year"), max_length=20,)
    total_records = models.IntegerField(null=True)
    file_type = models.CharField(max_length=150, null=True)
    action = models.CharField(_("Action"), max_length=50, null=True)
    is_approved = models.BooleanField(
        _("Is Approved"), null=True, blank=True, default=True)
    uploaded_by = models.CharField(_("Created By"), max_length=50,
                                   null=True, blank=True)
    file = models.FileField(
        _("File"), upload_to="uploads/", max_length=100, null=True)
    message = models.CharField(_("Rejection Message"), max_length=100)
    approved_on = models.DateTimeField(
        _("Approved On"), auto_now_add=True, null=True, blank=True)
    approved_by = models.CharField(
        _("Approved By"), max_length=50, null=True, blank=True)

    class Meta:
        db_table = "au_approval_data"
        verbose_name = "AU Approval Data"
        verbose_name_plural = "AU Approval Data"
