from django.contrib.auth.models import AbstractUser
from django.db import models

class UserProfile(AbstractUser):
    registered_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.username} - {self.registered_date}'

class Bank(models.Model):
    person_age = models.IntegerField()
    person_income = models.IntegerField()
    person_emp_exp = models.IntegerField()
    loan_amnt = models.IntegerField()
    loan_int_rate = models.IntegerField()
    loan_percent_income = models.IntegerField()
    cb_person_cred_hist_length = models.IntegerField()
    credit_score = models.IntegerField()
    person_gender = models.CharField(max_length=64)
    person_education = models.CharField(max_length=64)
    person_home_ownership = models.CharField(max_length=64)
    loan_intent = models.CharField(max_length=64)
    previous_loan_defaults_on_file = models.CharField(max_length=64)
    predict = models.FloatField(null=True, blank=True)
    probability = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f'{self.predict}%'