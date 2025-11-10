from django.contrib import admin
from django.http import HttpResponse
import csv
from import_export.admin import ImportExportModelAdmin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from .models import Question, QuestionOption, Species, UserAccess, AssignedSpecies, Evaluation, SpeciesGroup, SiteConfiguration#, EvaluationAnswer

# Fix groups import
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Species, SpeciesGroup

class SpeciesResource(resources.ModelResource):
    group = fields.Field(
        column_name='group',
        attribute='group',
        widget=ForeignKeyWidget(SpeciesGroup, 'name')
    )

    class Meta:
        model = Species
        import_id_fields = ['key']
        fields = ('key', 'name', 'group')  # explicitly declare


class EvaluationResource(resources.ModelResource):
    class Meta:
        model = Evaluation
        import_id_fields = ['id']
        fields = ['id', 'user_code', 'species_key', 'question_key', 'answer']

class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 1

class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionOptionInline]
    list_display = ('key', 'text')

class SpeciesAdmin(ImportExportModelAdmin):
    def log_import(self, *args, **kwargs):
        pass
    resource_class = SpeciesResource
    list_display = ('key', 'name', 'group')

class UserAccessAdmin(ImportExportModelAdmin):
    list_display = ['user_code', 'must_change_password', 'consent_accepted']
    filter_horizontal = ['groups']

class AssignedSpeciesAdmin(ImportExportModelAdmin):
    list_display = ('user_code', 'species_key')
    list_filter = ('user_code',)

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
class EvaluationAdmin(ImportExportModelAdmin):
    resource_class = EvaluationResource
    list_display = ['user_code', 'species_key', 'question_key', 'answer']
    actions = [export_evaluations_csv]

# Add maintenance mode configuration
@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ("maintenance_mode",)


###
from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse
from django.db.models import Count
from django.utils.html import format_html
from django.urls import path
from django.utils.safestring import mark_safe
import json, io, zipfile
@staff_member_required
def dashboard_view(request):
    total_records = Species.objects.values('key').distinct().count()
    total_respondents = Evaluation.objects.values('user_code').distinct().count()
    total_species = Evaluation.objects.values('species_key').distinct().count()
    total_experts = UserAccess.objects.values('user_code').distinct().count()

    #questions = Question.objects.all()
    questions = Question.objects.exclude(text__iexact="Comments")
    chart_data = []
    for q in questions:
        answers = (
            Evaluation.objects.filter(question_key=q.key)
            .values('answer')
            .annotate(count=Count('answer'))
            .order_by('answer')
        )
        labels = [a['answer'] for a in answers]
        counts = [a['count'] for a in answers]

        chart_data.append({
            'question': q.text,
            'labels': labels,
            'counts': counts,
        })

    # Convert to safe JSON for the template
    chart_data_json = mark_safe(json.dumps(chart_data))

    context = {
        'title': 'Evaluation Dashboard',
        'total_respondents': total_respondents,
        'total_species': total_species,
        'total_records': total_records,
        'total_experts': total_experts,
        'chart_data': chart_data_json,
    }

    return TemplateResponse(request, "admin/dashboard.html", context)

@staff_member_required
def download_data_and_code(request):
    """Generate CSV exports + R script in a zip file."""
    buffer = io.BytesIO()

    # Create an in-memory ZIP file
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:

        # 1. Evaluations CSV
        eval_csv = io.StringIO()
        writer = csv.writer(eval_csv)
        writer.writerow(["user_code", "species_key", "question_key", "answer"])
        for e in Evaluation.objects.all():
            writer.writerow([e.user_code, e.species_key, e.question_key, e.answer])
        zip_file.writestr("evaluations.csv", eval_csv.getvalue())

        # 2. Species CSV
        species_csv = io.StringIO()
        writer = csv.writer(species_csv)
        writer.writerow(["key", "name", "group"])
        for s in Species.objects.select_related("group").all():
            writer.writerow([s.key, s.name, getattr(s.group, "name", "")])
        zip_file.writestr("species.csv", species_csv.getvalue())

        # 3. Users CSV
        users_csv = io.StringIO()
        writer = csv.writer(users_csv)
        writer.writerow(["user_code", "must_change_password", "consent_accepted"])
        for u in UserAccess.objects.all():
            writer.writerow([u.user_code, u.must_change_password, u.consent_accepted])
        zip_file.writestr("users.csv", users_csv.getvalue())

        # 4. Questions CSV
        questions_csv = io.StringIO()
        writer = csv.writer(questions_csv)
        writer.writerow(["key", "text"])
        for q in Question.objects.all():
            writer.writerow([q.key, q.text])
        zip_file.writestr("questions.csv", questions_csv.getvalue())

        # 5. R Script
        r_script = """\
# --- Example R Script ---
# Load CSV files
evaluations <- read.csv("evaluations.csv")
species <- read.csv("species.csv")
users <- read.csv("users.csv")
questions <- read.csv("questions.csv")

# Example: merge and inspect
head(evaluations)
summary(species)
"""
        zip_file.writestr("analysis_script.R", r_script)
        # r_script_path = os.path.join(settings.BASE_DIR, "static", "analysis_script.R")
        # if os.path.exists(r_script_path):
        #     with open(r_script_path, "r", encoding="utf-8") as f:
        #         r_code = f.read()
        #     zip_file.writestr("analysis_script.R", r_code)
        # else:
        #     zip_file.writestr("analysis_script.R", "# R script not found in static folder.\n")

    # Prepare response
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="evaluation_data_bundle.zip"'
    return response

# Extend admin URLs safely (no recursion)
def get_admin_urls(urls):
    def wrap(view):
        return admin.site.admin_view(view)

    custom_urls = [
        path("dashboard/", wrap(dashboard_view), name="dashboard"),
        path("download-data/", wrap(download_data_and_code), name="download_data"),
    ]
    return custom_urls + urls

# Save the original method before overriding
original_get_urls = admin.site.get_urls
admin.site.get_urls = lambda: get_admin_urls(original_get_urls())