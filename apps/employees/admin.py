from django.contrib import admin
from apps.employees.models import Employee

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "store")
    search_fields = ("first_name", "last_name", "email")


admin.site.register(Employee, EmployeeAdmin)