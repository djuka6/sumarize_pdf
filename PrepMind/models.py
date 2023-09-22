from django.db import models


class SavedResponse(models.Model):
    question = models.TextField()
    answer = models.TextField()

    class Meta:
        app_label = "PrepMind"
