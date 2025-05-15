from django.contrib import admin

# Register your models here.
from .models import Question, QuestionOption, Species, UserAccess, AssignedSpecies

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