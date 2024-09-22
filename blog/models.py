from django.db import models
from  django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from tinymce.models import HTMLField

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = HTMLField(null=True,blank=True)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail',kwargs={'pk':self.pk})

class Website(models.Model):
    web_name = models.CharField(max_length=100)
    web_url = models.URLField(max_length=300)

    def __str__(self):
        return self.web_name