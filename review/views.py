from django.shortcuts import render, redirect, get_object_or_404
from .models import AssignedSpecies, Species, Question, QuestionOption, Evaluation, UserAccess, SkippedSpecies
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.templatetags.static import static #maybe remove
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.timezone import now
from django import forms

User = get_user_model()

base_url = "https://mpaeu-dist.s3.amazonaws.com/review/"

class PasswordChangeWithConsentForm(PasswordChangeForm):
    consent_accepted = forms.BooleanField(
        required=True,
        label="I agree to the terms of participation and data usage."
    )

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

@login_required
def force_password_change(request):
    error_message = None

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        consent_checked = request.POST.get('consent_checkbox') == 'on'

        if new_password and new_password == confirm_password and consent_checked:
            user = request.user
            user.set_password(new_password)
            user.save()

            access = UserAccess.objects.get(user_code=user.username)
            access.must_change_password = False
            access.consent_accepted = True
            access.consent_timestamp = now()
            access.consent_ip = get_client_ip(request)
            access.save()

            update_session_auth_hash(request, user)

            return redirect('evaluate_next_species')
        else:
            error_message = "Please ensure the passwords match and the consent box is checked."

    return render(request, 'force_password_change.html', {
        'error_message': error_message
    })

@login_required
def evaluate_next_species(request):
    user_code = request.user.username  # Assuming username matches user_code
    error = None

    # Step 1: Find assigned species not fully evaluated
    assigned = AssignedSpecies.objects.filter(user_code=user_code)

    try:
        for assignment in assigned:
            species_key = assignment.species_key
            required_questions = Question.objects.filter(is_required=True)
            required_keys = required_questions.values_list('key', flat=True)

            num_required = required_questions.count()
            num_answers = Evaluation.objects.filter(
                user_code=user_code,
                species_key=species_key,
                question_key__in=required_keys
            ).count()

            if num_answers < num_required:
                current_species = get_object_or_404(Species, key=species_key)
                break
        else:
            return redirect("evaluation_complete", user_code=user_code)
    except Exception as e:
        # Log or print for debugging
        print(f"Exception during species evaluation loop: {e}")
        raise


    questions = Question.objects.all()

    if request.method == "POST":
        # Validate required questions
        missing_answers = [
            question for question in questions
            if question.is_required and not request.POST.get(f"question_{question.key}")
        ]

        if missing_answers:
            error = "Please answer all required questions before submitting."
        else:
            for question in questions:
                answer = request.POST.get(f"question_{question.key}")
                if answer:
                    Evaluation.objects.update_or_create(
                        user_code=user_code,
                        species_key=current_species.key,
                        question_key=question.key,
                        defaults={'answer': answer}
                    )
            return redirect('evaluate_next_species')  # Go to next species


    context = {
        'species': current_species,
        'questions': questions,
        'error': error, 
        'current': static(f"{base_url}taxonid={species_key}_current.tif"),
        'current_th': static(f"{base_url}taxonid={species_key}_current_th.tif"),
        'points': static(f"{base_url}taxonid={species_key}_pts.csv"),
        'future': static(f"{base_url}taxonid={species_key}_current_th_ssp1.tif"),
        'future_b': static(f"{base_url}taxonid={species_key}_current_th_ssp3.tif"),
        'others': static(f"{base_url}taxonid={species_key}_others.png"),
    }
    return render(request, "evaluate.html", context)

@login_required
def species_overview(request):
    user_code = request.user.username
    required_questions = Question.objects.filter(is_required=True)
    required_keys = required_questions.values_list('key', flat=True)
    total_required = required_questions.count()

    # Species explicitly assigned to this user
    assigned_keys = AssignedSpecies.objects.filter(
        user_code=user_code
    ).values_list('species_key', flat=True)

    assigned_species = Species.objects.filter(key__in=assigned_keys)

    pending, completed = [], []

    # Evaluate assigned species
    for sp in assigned_species:
        answered = Evaluation.objects.filter(
            user_code=user_code,
            species_key=sp.key,
            question_key__in=required_keys
        ).count()
        if answered >= total_required:
            completed.append(sp)
        else:
            pending.append(sp)

    # Extra: species evaluated by the user but NOT assigned
    evaluated_keys = Evaluation.objects.filter(
        user_code=user_code
    ).values_list('species_key', flat=True).distinct()

    extra_keys = set(evaluated_keys) - set(assigned_keys)

    extra_species = Species.objects.filter(key__in=extra_keys)

    context = {
        "pending_species": pending,
        "completed_species": completed,
        "extra_species": extra_species,
    }
    return render(request, "species_overview.html", context)


@login_required
def evaluation_complete(request, user_code):
    access = get_object_or_404(UserAccess, user_code=user_code)
    groups = access.groups.all()

    # Already evaluated
    evaluated_species_keys = Evaluation.objects.filter(
        user_code=user_code
    ).values_list('species_key', flat=True)

    # Show unassigned species in same group not yet evaluated
    available_species = Species.objects.filter(group__in=groups).exclude(key__in=evaluated_species_keys).order_by('name')

    group_names = ", ".join([group.name for group in groups])

    return render(request, "done.html", {
        "user_code": user_code,
        "groups": groups,
        "group_names": group_names, 
        "species_list": available_species
    })

@login_required
def evaluate_species(request, species_key):
    user_code = request.user.username
    current_species = get_object_or_404(Species, key=species_key)
    questions = Question.objects.all()

    # Check if species is assigned to user
    is_assigned = AssignedSpecies.objects.filter(
        user_code=user_code,
        species_key=species_key
    ).exists()

    error = None

    if request.method == "POST":
        if request.POST.get("submit") == "skip":
            # Mark this species as skipped
            SkippedSpecies.objects.get_or_create(user_code=user_code, species_key=species_key)

            # Find next species in user's group, excluding evaluated, skipped, and current species
            access = get_object_or_404(UserAccess, user_code=user_code)
            groups = access.groups.all()

            # Get species keys fully evaluated by user
            required_questions = Question.objects.filter(is_required=True)
            required_keys = required_questions.values_list('key', flat=True)
            total_required = required_questions.count()

            evaluated_keys = []
            for sp in Species.objects.filter(group__in=groups):
                answers_count = Evaluation.objects.filter(
                    user_code=user_code,
                    species_key=sp.key,
                    question_key__in=required_keys
                ).count()
                if answers_count >= total_required:
                    evaluated_keys.append(sp.key)

            skipped_keys = SkippedSpecies.objects.filter(user_code=user_code).values_list('species_key', flat=True)

            next_species = Species.objects.filter(group__in=groups) \
                .exclude(key__in=evaluated_keys) \
                .exclude(key__in=skipped_keys) \
                .exclude(key=species_key) \
                .first()

            if next_species:
                return redirect('evaluate_species', species_key=next_species.key)
            else:
                return redirect('evaluation_complete', user_code=user_code)

        # Validate: Check that all questions have answers
        missing_answers = [
            question for question in questions
            if question.is_required and not request.POST.get(f"question_{question.key}")
        ]

        if missing_answers:
            error = "Please answer all questions before submitting." 
        else:
            # Process submitted answers
            for question in questions:
                answer = request.POST.get(f"question_{question.key}")
                if answer:
                    Evaluation.objects.update_or_create(
                        user_code=user_code,
                        species_key=species_key,
                        question_key=question.key,
                        defaults={'answer': answer}
                    )

            # After saving answers, go to next uncompleted species in same group
            access = get_object_or_404(UserAccess, user_code=user_code)
            groups = access.groups.all()
            evaluated_keys = Evaluation.objects.filter(user_code=user_code).values_list('species_key', flat=True)
            next_species = Species.objects.filter(group__in=groups).exclude(key__in=evaluated_keys).first()

            if next_species:
                return redirect('evaluate_species', species_key=next_species.key)
            else:
                return redirect('evaluation_complete', user_code=user_code)

    context = {
        'species': current_species,
        'questions': questions,
        'from_extra': not is_assigned, 
        'error': error, 
        'current': static(f"{base_url}taxonid={species_key}_current.tif"),
        'current_th': static(f"{base_url}taxonid={species_key}_current_th.tif"),
        'points': static(f"{base_url}taxonid={species_key}_pts.csv"),
        'future': static(f"{base_url}taxonid={species_key}_current_th_ssp1.tif"),
        'future_b': static(f"{base_url}taxonid={species_key}_current_th_ssp3.tif"),
        'others': static(f"{base_url}taxonid={species_key}_others.png"),
    }
    return render(request, "evaluate.html", context)