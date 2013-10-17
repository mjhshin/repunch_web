from django import forms
from models import Employee
from libs.repunch import rputils
from repunch import settings
import os

from libs.repunch.validators import required
from parse.apps.stores import ACCESS_ADMIN, ACCESS_PUNCHREDEEM,\
ACCESS_NONE

# format the choices 
ACL_CHOICES = (
    (ACCESS_ADMIN[0], "Full Admin Access"),
    (ACCESS_PUNCHREDEEM[0], "Allow Punch/Redeem"),
)

class EmployeeForm(forms.Form):
    first_name = forms.CharField(max_length=50, 
        validators=[required])
    last_name = forms.CharField(max_length=50,
        validators=[required])
    acl = forms.ChoiceField(choices=ACL_CHOICES)
        
class EmployeeAvatarForm(forms.Form):
    employee_avatar = forms.FileField()
        
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
