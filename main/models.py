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

class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    name = models.CharField(max_length=20, null=False, blank=False, default='Treino')

    def __str__(self):
        return f"{self.name}"

class Exercise(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='exercises', default=None)
    name = models.CharField(max_length=50, blank=False, null=False, default='exercise')
    position = models.CharField(max_length=50, blank=False, null=False, default='midrange-r')
    reps = models.IntegerField( validators=[MinValueValidator(1), MaxValueValidator(999)], null=False, blank=False, default=10)
    makes = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    accuracy = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        blank=True
    )
    checked = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.reps:
            self.accuracy = (self.makes / self.reps) * 100
        super().save(*args, **kwargs)



    def __str__(self):
        return f"{self.name} ({self.makes}/{self.reps}) - {self.accuracy or 0}%"
    
class DoneSession(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True)
    duration = models.IntegerField()
    date_finished = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"sessao finalizada: {self.session.name}"

class Tasks(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    name = models.CharField(max_length=20, blank=False, null=False, default='Tarefa')
    checked = models.BooleanField(default=False)


    def __str__(self):
        return f"Tarefa: {self.name}"





