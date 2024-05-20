from django.db import models

class Member(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Activity(models.Model):
    date = models.CharField(max_length=10)
    activity_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.activity_name} ({self.date})"

class ActivityLog(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    participant = models.ForeignKey(Member, on_delete=models.CASCADE)
    duration = models.IntegerField()  # duration in minutes

    def __str__(self):
        return f"{self.participant.name} - {self.activity.activity_name} ({self.activity.date})"
