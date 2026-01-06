import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Document(models.Model):
    file = models.FileField(upload_to='documents/')
    content = models.TextField(blank=True)
    tags = models.ManyToManyField('Tag', blank=True)

    def __str__(self):
        return self.file.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    

class Philosophy(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='prompt_module/philosophy/')
    is_global = models.BooleanField(default=True)  # True = always injected
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{'[GLOBAL] ' if self.is_global else ''}{self.title}"



class Persona(models.Model):
    title = models.CharField(max_length=255)  # e.g., "Persona – Motivator"
    file = models.FileField(upload_to='prompt_module/persona/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('client', 'Client'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Voice(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='prompt_module/voice/')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Tone(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='prompt_module/tone/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# class ChatSession(models.Model):
#     title = models.CharField(max_length=255, blank=True)
#     created_at = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return self.title if self.title else f"Chat {self.pk}"

#     class Meta:
#         ordering = ['-created_at']


class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title if self.title else f"Chat {self.pk}"

    class Meta:
        ordering = ['-created_at']
class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, related_name="messages", on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[('user', 'User'), ('assistant', 'Assistant')])
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.role.title()} | {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['timestamp']