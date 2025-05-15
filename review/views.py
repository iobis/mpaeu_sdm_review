from django.shortcuts import render, redirect, get_object_or_404
from .models import AssignedSpecies, Species, Question, QuestionOption, Evaluation
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.templatetags.static import static #maybe remove

User = get_user_model()

@login_required
def evaluate_next_species(request):
    user_code = request.user.username  # Assuming username matches user_code

    # Step 1: Find assigned species not fully evaluated
    assigned = AssignedSpecies.objects.filter(user_code=user_code)

    for assignment in assigned:
        species_key = assignment.species_key
        num_questions = Question.objects.count()
        num_answers = Evaluation.objects.filter(
            user_code=user_code,
            species_key=species_key
        ).count()
        if num_answers < num_questions:
            current_species = get_object_or_404(Species, key=species_key)
            break
    else:
        # All species evaluated
        return render(request, "done.html")

    questions = Question.objects.all()

    if request.method == "POST":
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
        #'cog_url': static(f"review/species/taxonid=102279_current_cog.tif")
        'current': "https://mpaeu-dist.s3.amazonaws.com/results/species/taxonid=1005391/model=mpaeu/predictions/taxonid=1005391_model=mpaeu_method=esm_scen=current_cog.tif",
        'future': "https://mpaeu-dist.s3.amazonaws.com/results/species/taxonid=1005391/model=mpaeu/predictions/taxonid=1005391_model=mpaeu_method=esm_scen=ssp370_dec100_cog.tif"
    }
    return render(request, "evaluate.html", context)

@login_required
def species_overview(request):
    user_code = request.user.username          # ↳ assumes username == user_code
    total_q = Question.objects.count()

    # all species explicitly assigned to this user
    assigned_keys = AssignedSpecies.objects.filter(
        user_code=user_code
    ).values_list('species_key', flat=True)

    assigned_species = Species.objects.filter(key__in=assigned_keys)

    pending, completed = [], []
    for sp in assigned_species:
        answered = Evaluation.objects.filter(
            user_code=user_code,
            species_key=sp.key
        ).count()
        if answered >= total_q:
            completed.append(sp)
        else:
            pending.append(sp)

    context = {
        "pending_species": pending,
        "completed_species": completed,
    }
    return render(request, "species_overview.html", context)