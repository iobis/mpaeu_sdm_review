from django.contrib import admin
from django.http import HttpResponse
import csv
from import_export.admin import ImportExportModelAdmin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from .models import Question, QuestionOption, Species, UserAccess, AssignedSpecies, Evaluation, SpeciesGroup#, EvaluationAnswer

class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 1

class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionOptionInline]
    list_display = ('key', 'text')

class SpeciesAdmin(ImportExportModelAdmin):
    list_display = ('key', 'name', 'group')

class UserAccessAdmin(ImportExportModelAdmin):
    list_display = ['user_code', 'must_change_password', 'consent_accepted']
    filter_horizontal = ['groups']

class AssignedSpeciesAdmin(ImportExportModelAdmin):
    list_display = ('user_code', 'species_key')

class SpeciesGroupAdmin(ImportExportModelAdmin):
    list_display = ['name']

# Register all models with the admin
admin.site.register(Question, QuestionAdmin)
admin.site.register(Species, SpeciesAdmin)
admin.site.register(UserAccess, UserAccessAdmin)
admin.site.register(AssignedSpecies, AssignedSpeciesAdmin)
admin.site.register(SpeciesGroup, SpeciesGroupAdmin)

# To be able to use import in the user admin
class CustomUserAdmin(ImportExportModelAdmin, UserAdmin):
    pass

# Unregister the original User admin
admin.site.unregister(User)

# Register the User model with your custom admin
admin.site.register(User, CustomUserAdmin)

@admin.action(description="Export evaluations as CSV")
def export_evaluations_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="evaluations.csv"'

    writer = csv.writer(response)
    writer.writerow(['user_code', 'species_key', 'question', 'answer'])

    # Build a lookup dictionary for question text
    question_lookup = {
        q.key: q.text for q in Question.objects.all()
    }

    for evaluation in queryset:
        question_text = question_lookup.get(evaluation.question_key, evaluation.question_key)
        writer.writerow([
            evaluation.user_code,
            evaluation.species_key,
            question_text,
            evaluation.answer
        ])

    return response

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ['user_code', 'species_key', 'question_key', 'answer']
    actions = [export_evaluations_csv]