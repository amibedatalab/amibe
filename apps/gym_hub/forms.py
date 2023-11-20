from django import forms
from apps.gym_hub.models import (FileUpload,UploadDueBook,MasterRate,
                                   UploadBlueBook,DataUploadTask,TempTable
                                   ,CollectionUpdate,ErrorTable)



class FileIUploadForm(forms.ModelForm):
    OPERATION_ACTION=[
        ('UPLOAD','UPLOAD'),
        ('APPEND','APPEND'),
        ('UPDATE','UPDATE'),
        ('REPLACE','REPLACE'),
    ]
    FINANCIAL_YEAR = [
        ('2016-2017', '2016-2017'),
        ('2017-2018', '2017-2018'),
        ('2018-2019', '2018-2019'),
        ('2019-2020', '2019-2020'),
        ('2020-2021', '2020-2021'),
        ('2021-2022', '2021-2022'),
        ('2022-2023', '2022-2023'),
        ('2023-2024', '2023-2024'),
        ('2024-2025', '2024-2025'),
        ('2025-2026', '2025-2026'),
        ('2026-2027', '2026-2027'),
        ('2027-2028', '2027-2028'),
        ('2028-2029', '2028-2029'),
        ('2029-2030', '2029-2030'),
        ('2030-2031', '2030-2031'),
        ('2031-2032', '2031-2032'),
        ('2032-2033', '2032-2033'),
        ('2033-2034', '2033-2034'),
        ('2034-2035', '2034-2035'),
        ('2035-2036', '2035-2036'),
        ('2036-2037', '2036-2037'),
        ('2037-2038', '2037-2038'),
        ('2038-2039', '2038-2039'),
        ('2039-2040', '2039-2040'),
        ('2040-2041', '2040-2041'),
        ('2041-2042', '2041-2042'),
        ('2042-2043', '2042-2043'),
        ('2043-2044', '2043-2044'),
        ('2044-2045', '2044-2045'),
        ('2045-2046', '2045-2046'),
        ('2046-2047', '2046-2047'),
        ('2047-2048', '2047-2048'),
        ('2048-2049', '2048-2049'),
        ('2049-2050', '2049-2050'),
        ('2050-2051', '2050-2051')  # Extending to 2051
    ]


    
    action=forms.ChoiceField(choices=OPERATION_ACTION)
    financial_year=forms.ChoiceField(choices=FINANCIAL_YEAR)
    class Meta:
        model= FileUpload
        fields = ["file","action","financial_year"]
    
    def clean_file(self):
        file=self.cleaned_data['file']
        allowed_extention=['.xlsx','.xls','.xlsb','.xlsm']
        file_ext=file.name.split('.')[-1].lower()
        
        if not any(file_ext==ext[1:] for ext in allowed_extention):
            raise forms.ValidationError("Invalid file type. Allowed types: EXCEL")
        
        if not file_ext:
            corrected_filename=f"{file.name}.xlsx"
            file.name=corrected_filename
        return file

class FileUploadMasterForm(forms.ModelForm):

    ACTION=[
        ('UPLOAD','UPLOAD '),
        ('APPEND','APPEND'),
    ]
    action=forms.ChoiceField(choices=ACTION)
    class Meta:
        model=FileUpload
        fields=["file","action"]

    def clean_file(self):
        file=self.cleaned_data['file']
        allowed_extention=['.xlsx','.xls','.xlsb','.xlsm']
        file_ext=file.name.split('.')[-1].lower()
        
        if not any(file_ext == ext[1:] for ext in allowed_extention):
            raise forms.ValidationError(
                "Invalid file type. Allowed types: EXCEL")

        if not file_ext:
            corrected_filename=f"{file.name}.xlsx"
            file.name=corrected_filename
        return file 
class FileUploadCollectionFlagForm(forms.ModelForm):

    class Meta:
        model=FileUpload
        fields=["file"]

    def clean_file(self):
        file=self.cleaned_data['file']
        allowed_extention=['.xlsx','.xls','.xlsb','.xlsm']
        file_ext=file.name.split('.')[-1].lower()
        
        if not any(file_ext == ext[1:] for ext in allowed_extention):
            raise forms.ValidationError(
                "Invalid file type. Allowed types: EXCEL")

        if not file_ext:
            corrected_filename=f"{file.name}.xlsx"
            file.name=corrected_filename
        return file 
    
class TempTableForm(forms.ModelForm):
    class Meta:
        model=TempTable
        fields="__all__"

class UploadDueBookForm(forms.ModelForm):
    
    class Meta:
        model:UploadDueBook
        fields="__all__"

    def clean_file(self):
        file=self.cleaned_data['file']
        allowed_extention=['.xlsx','.xls']
        file_ext=file.name.split('.')[-1].lower()
        
        if not any(file_ext==ext[1:] for ext in allowed_extention):
            raise forms.ValidationError("Invalid file type. Allowed types: EXCEL")
        
        if not file_ext:
            corrected_filename=f"{file.name}.xlsx"
            file.name=corrected_filename
        return file
    
class UploadBlueBookForm(forms.ModelForm):
    
    class Meta:
        model:UploadBlueBook
        fields="__all__"

    def clean_file(self):
        file=self.cleaned_data['file']
        allowed_extention=['.xlsx','.xls']
        file_ext=file.name.split('.')[-1].lower()
        
        if not any(file_ext==ext[1:] for ext in allowed_extention):
            raise forms.ValidationError("Invalid file type. Allowed types: EXCEL")
        
        if not file_ext:
            corrected_filename=f"{file.name}.xlsx"
            file.name=corrected_filename
        return file
    
    
class MasterRateForm(forms.ModelForm):
    class Meta:
        model=MasterRate
        fields="__all__"

    def clean_file(self):
        file=self.cleaned_data['file']
        allowed_extention=['.xlsx','.xls']
        file_ext=file.name.split('.')[-1].lower()

        if not any(file_ext==ext[1:] for ext in allowed_extention):
            raise forms.ValidationError("Invalid file type. Allowed types: EXCEL")

        if not file_ext:
            corrected_filename=f"{file.name}.xlsx"
            
            file.name=corrected_filename
        return file



class ErrorTableForm(forms.ModelForm):
    class Meta:
        model=ErrorTable
        fields="__all__"


class ApprovalForm(forms.Form):
    approval_message = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Enter approval message (optional)'}),
        required=False
    )

class RejectionForm(forms.Form):
     rejection_message = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter rejection message', 'class': 'form-control'}),
        required=True
    )


class CollectionFlagForm(forms.Form):
    class Meta:
        model=CollectionUpdate
        fields ="__all__"
    pass