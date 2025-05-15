from django.contrib import admin
from django.http import HttpResponse
import csv

# Register your models here.
from .models import Question, QuestionOption, Species, UserAccess, AssignedSpecies#, EvaluationAnswer

class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 1

class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionOptionInline]
    list_display = ('key', 'text')

class SpeciesAdmin(admin.ModelAdmin):
    list_display = ('key', 'name', 'group')

class UserAccessAdmin(admin.ModelAdmin):
    list_display = ('user_code', 'group')

class AssignedSpeciesAdmin(admin.ModelAdmin):
    list_display = ('user_code', 'species_key')

# Register all models with the admin
admin.site.register(Question, QuestionAdmin)
admin.site.register(Species, SpeciesAdmin)
admin.site.register(UserAccess, UserAccessAdmin)
admin.site.register(AssignedSpecies, AssignedSpeciesAdmin)

# Answers
# class EvaluationAnswerAdmin(admin.ModelAdmin):
#     list_display = ("user", "species", "question", "answer")

#     actions = ["export_as_csv"]

#     def export_as_csv(self, request, queryset):
#         response = HttpResponse(content_type="text/csv")
#         response["Content-Disposition"] = "attachment; filename=evaluation_results.csv"

#         writer = csv.writer(response)
#         writer.writerow(["User", "Species", "Question", "Answer"])

#         for answer in queryset:
#             writer.writerow([
#                 answer.user.username,
#                 answer.species.name,
#                 answer.question.text,
#                 answer.answer
#             ])

#         return response

#     export_as_csv.short_description = "Export selected results as CSV"

# admin.site.register(EvaluationAnswer, EvaluationAnswerAdmin)