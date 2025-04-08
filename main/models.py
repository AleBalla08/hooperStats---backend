from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator



class ProfileModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_photo = models.ImageField(
        upload_to='avatars/', 
        blank=True, 
        default='avatars/profile-default.svg'
    )
    bio = models.TextField(max_length=250, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    height = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0.5),
            MaxValueValidator(2.5)
        ]
    )

class Exercise(models.Model):
    session_id = models.CharField(max_length=100, null=False, blank=False, default=0)
    name = models.CharField(max_length=50, blank=False, null=False, default='exercise')
    reps = models.IntegerField( validators=[MinValueValidator(1), MaxValueValidator(999)], null=False, blank=False, default=10)
    makes = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    accuracy = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        blank=True
    )
    checked = models.CharField(max_length=1, null=False, blank=False, default=0)

    def __str__(self):
        return f"{self.name} ({self.makes}/{self.reps}) - {self.accuracy or 0}%"

class Session(models.Model):
    name = models.CharField(max_length=20, null=False, blank=False, default='Treino')
    exercises = models.ManyToManyField(Exercise)

    def __str__(self):
        return f"{self.name}"
    
class DoneSession(models.Model):
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING)
    duration = models.DurationField()
    date_finished = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"sessao finalizada: {self.session.name}"

class Tasks(models.Model):
    name = models.CharField(max_length=20, blank=False, null=False, default='Tarefa')
    checked = models.CharField(max_length=1, null=False, blank=False, default=0)

    def __str__(self):
        return f"Tarefa: {self.name}"





