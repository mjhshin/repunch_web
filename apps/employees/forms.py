from django import forms
from models import Employee
from libs.repunch import rputils
from repunch import settings
import os

class EmployeeForm(forms.Form):
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    email = forms.CharField(max_length=255)
        
class EmployeeAvatarForm(forms.Form):
    employee_avatar = forms.ImageField()
        
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
