from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group
from apps.authentication.models import User
from apps.gym_hub.models import DataUploadTask,ApprovalData,UploadDueBook,UploadBlueBook,CollectionUpdate
from apps.authentication.forms import CustomUserCreationForm
class CustomGroupAdmin(GroupAdmin):
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'permissions':
            qs = kwargs.get('queryset', db_field.remote_field.model.objects)

            # Exclude common permissions for all users
            common_permissions = (
                'add_permission',
                'change_permission',
                'delete_permission',
                'view_permission',

                'add_contenttype',
                'change_contenttype',
                'delete_contenttype',
                'view_contenttype',

                'add_session',
                'delete_session',
                'change_session',
                'view_session',

                'add_logentry',
                'change_logentry',
                'delete_logentry',
                'view_logentry',

                'add_temptable',
                'change_temptable',
                'delete_temptable',
                'view_temptable',

                'add_temptablebb',
                'change_temptablebb',
                'delete_temptablebb',
                'view_temptablebb',

                'add_errortable',
                'change_errortable',
                'delete_errortable',
                'view_errortable',

                'add_taskresult',
                'change_taskresult',
                'delete_taskresult',
                'view_taskresult',

                'add_chordcounter',
                'change_chordcounter',
                'delete_chordcounter',
                'view_chordcounter',

                'add_solarschedule',
                'change_solarschedule',
                'delete_solarschedule',
                'view_solarschedule',

                'add_periodictask',
                'change_periodictask',
                'delete_periodictask',
                'view_periodictask',

                'add_periodictasks',
                'change_periodictasks',
                'delete_periodictasks',
                'view_periodictasks',

                'add_crontabschedule',
                'change_crontabschedule',
                'delete_crontabschedule',
                'view_crontabschedule',

                'add_intervalschedule',
                'change_intervalschedule',
                'delete_intervalschedule',
                'view_intervalschedule',

                'add_clockedschedule',
                'change_clockedschedule',
                'delete_clockedschedule',
                'view_clockedschedule',

                'add_datauploadtask',
                'change_datauploadtask',
                'delete_datauploadtask',
                'view_datauploadtask',
            )

            # If the logged-in user is not a superuser, exclude additional permissions
            if not request.user.is_superuser:
                additional_permissions = (
                    # Add additional permissions here
                    'delete_group',
                    'delete_user',
                    'delete_channelpartner',
                    'add_masterrate',
                    'delete_approverpermission',
                    'delete_collectionupdate',
                    'add_au_masterrate',
                    'change_au_masterrate',
                    'delete_au_masterrate',
                    'add_au_uploadebluebook',
                    'change_au_uploadebluebook',
                    'delete_au_uploadebluebook',

                    'add_au_uploadeduebook',
                    'change_au_uploadeduebook',
                    'delete_au_uploadeduebook',
                    'delete_fileupload',
                    'delete_uploadbluebook',
                    'delete_uploadduebook',
                    'delete_masterrate',

                )
                common_permissions += additional_permissions

            qs = qs.exclude(codename__in=common_permissions)

            # Avoid a major performance hit resolving permission names which
            # triggers a content_type load:
            kwargs['queryset'] = qs.select_related('content_type')

        return super().formfield_for_manytomany(db_field, request=request, **kwargs)


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    list_display = ('email', 'first_name', 'last_name', 'is_active')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password','first_name','last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups')}),
    )
    # this is used to hide superuser when any other user is loggedin on admin site
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.exclude(is_superuser=True)
        return qs

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email", "password1", "password2", 'first_name', 'last_name', "is_staff",
                    "is_active", "is_superuser","groups"
                )
            }
        ),
    )
     # to save username uniquely without filling it from admin
    def save_model(self, request, obj, form, change):
        obj.username = obj.email
        super().save_model(request, obj, form, change)
    search_fields = ('email',)
    ordering = ('email',)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)

        # If the logged-in user is not a superuser, remove the 'is_superuser' field from the fieldsets.
        if not request.user.is_superuser:
            for fieldset in fieldsets:
                fieldset[1]['fields'] = [field for field in fieldset[1]['fields'] if field != 'is_superuser']

        return fieldsets


    UserAdmin.fieldsets + add_fieldsets


admin.site.unregister(Group)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Group, CustomGroupAdmin)
#admin.site.register(DataUploadTask)
#admin.site.register(ApprovalData)
#admin.site.register(UploadDueBook)
#admin.site.register(UploadBlueBook)
#admin.site.register(CollectionUpdate)
