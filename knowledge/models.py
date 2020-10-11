from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class KnowledgeBase(models.Model):

    name = models.CharField(max_length=128, unique=True)
    shop_id = models.CharField(max_length=255, unique=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    running_status = models.BooleanField(default=True)
    desc = models.CharField(max_length=512)

    users = models.ManyToManyField(User, related_name='users')

    class Meta:
        ordering = ('-id',)


class KnowledgeItem(models.Model):

    KNOWLEDGE_SCOPE = (
        (0, '售前'),
        (1, '售中'),
        (1, '售后'),
    )

    knowledge_base = models.ForeignKey(
        KnowledgeBase, on_delete=models.SET_NULL, null=True,
        related_name='knowledge_list')
    question = models.CharField(max_length=512)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    scope = models.IntegerField(choices=KNOWLEDGE_SCOPE)

    class Meta:
        ordering = ('-id',)


class Answer(models.Model):
    knowledge_item = models.ForeignKey(
        KnowledgeItem, on_delete=models.SET_NULL, null=True,
        related_name='answers')
    content = models.TextField()


class SimilarQuestion(models.Model):
    knowledge_item = models.ForeignKey(
        KnowledgeItem, on_delete=models.SET_NULL, null=True,
        related_name='similar_questions')
    content = models.TextField()
