from django.db import models
from django.utils.timezone import now

# Create your models here.
class SpeciesGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Species(models.Model):
    key = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    group = models.ForeignKey(SpeciesGroup, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class UserAccess(models.Model):
    user_code = models.CharField(max_length=100, unique=True)
    groups = models.ManyToManyField("SpeciesGroup")
    must_change_password = models.BooleanField(default=True)
    consent_accepted = models.BooleanField(default=False)
    consent_timestamp = models.DateTimeField(null=True, blank=True)
    consent_ip = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return self.user_code
    
class AssignedSpecies(models.Model):
    user_code = models.CharField(max_length=100)
    species_key = models.CharField(max_length=100)

    class Meta:
        unique_together = ('user_code', 'species_key')

class Question(models.Model):
    QUESTION_TYPES = [
        ('radio', 'Radio (Multiple Choice)'),
        ('text', 'Free Text'),
    ]

    key = models.CharField(max_length=100, unique=True)
    text = models.CharField(max_length=255)
    explanation = models.CharField(max_length=500, default='', blank=True, null=True)
    is_required = models.BooleanField(default=True)
    question_type = models.CharField(
        max_length=10,
        choices=QUESTION_TYPES,
        default='radio'
    )

    def __str__(self):
        return self.text
    
class Evaluation(models.Model):
    user_code = models.CharField(max_length=100)
    species_key = models.CharField(max_length=100)
    question_key = models.CharField(max_length=100)
    answer = models.CharField(max_length=255)

    class Meta:
        unique_together = ('user_code', 'species_key', 'question_key')

class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    value = models.CharField(max_length=300)

    def __str__(self):
        return f"{self.question.key}: {self.value}"
    
class SkippedSpecies(models.Model):
    user_code = models.CharField(max_length=100)
    species_key = models.CharField(max_length=100)

    class Meta:
        unique_together = ('user_code', 'species_key')