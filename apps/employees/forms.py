from django import forms
from models import Employee
from libs.repunch import rputils
from repunch import settings
import os

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        exclude = ('store', 'date_added', 'status', 'employee_avatar')
        
class EmployeeAvatarForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ('employee_avatar',)
        
    def save(self, force_insert=False, force_update=False, commit=True):    
            
        if self.instance != None:
            employee = Employee.objects.filter().get(id=self.instance.id)
            if employee.employee_avatar:
                try:                
                    employee.employee_avatar.delete()
                except Exception:
                    pass # do nothing, 
                
        employee = super(EmployeeAvatarForm, self).save()
        if employee != None:
            rputils.rescale(os.path.join(settings.MEDIA_ROOT, employee.employee_avatar.name))
        
        return employee