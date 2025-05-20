from django.contrib import admin
from django.http import HttpResponse
import csv
from import_export.admin import ImportExportModelAdmin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from .models import Question, QuestionOption, Species, UserAccess, AssignedSpecies#, EvaluationAnswer

class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 1

class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionOptionInline]
    list_display = ('key', 'text')

class SpeciesAdmin(ImportExportModelAdmin):
    list_display = ('key', 'name', 'group')

class UserAccessAdmin(ImportExportModelAdmin):
    list_display = ('user_code', 'group')

class AssignedSpeciesAdmin(ImportExportModelAdmin):
    list_display = ('user_code', 'species_key')

# Register all models with the admin
admin.site.register(Question, QuestionAdmin)
admin.site.register(Species, SpeciesAdmin)
admin.site.register(UserAccess, UserAccessAdmin)
admin.site.register(AssignedSpecies, AssignedSpeciesAdmin)

# To be able to use import in the user admin
class CustomUserAdmin(ImportExportModelAdmin, UserAdmin):
    pass

# Unregister the original User admin
admin.site.unregister(User)

# Register the User model with your custom admin
admin.site.register(User, CustomUserAdmin)