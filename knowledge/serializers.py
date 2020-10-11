# -*- coding: utf-8 -*-

from rest_framework import serializers

from knowledge import models


# Serializers define the API representation.
class KnowledgeBaseSerializer(serializers.ModelSerializer):

    knowledge_list = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True)
    users = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = models.KnowledgeBase
        fields = '__all__'


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Answer
        fields = '__all__'


class SimilarQuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.SimilarQuestion
        fields = '__all__'


class KnowledgeItemSerializer(serializers.ModelSerializer):

    answers = AnswerSerializer(
        many=True)
    similar_questions = SimilarQuestionSerializer(
        many=True,)

    class Meta:
        model = models.KnowledgeItem
        fields = ['id', 'answers', 'similar_questions', 'knowledge_base',
                  'question', 'scope', 'created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        answers = validated_data.pop('answers')
        similar_questions = validated_data.pop('similar_questions')
        knowledge_item = models.KnowledgeItem.objects.create(**validated_data)
        for answer in answers:
            models.Answer.objects.create(
                knowledge_item=knowledge_item, **answer)
        for similar_question in similar_questions:
            models.SimilarQuestion.objects.create(
                knowledge_item=knowledge_item, **similar_question)
        return knowledge_item

    def update(self, instance, validated_data):
        answers = validated_data.pop('answers')
        similar_questions = validated_data.pop('similar_questions')
        instance = super().update(instance, validated_data)
        models.Answer.objects.filter(knowledge_item=instance).delete()
        models.SimilarQuestion.objects.filter(knowledge_item=instance).delete()
        for answer in answers:
            models.Answer.objects.create(
                knowledge_item=instance, **answer)
        for similar_question in similar_questions:
            models.SimilarQuestion.objects.create(
                knowledge_item=instance, **similar_question)
        return instance
