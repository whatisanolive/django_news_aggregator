from rest_framework import serializers

from articles.models import Article, Comment, Vote
from django.db.models import Sum
from django.db.models.functions import Coalesce

class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='user.username', read_only=True)
    author_profile_pic = serializers.CharField(source='user.profile.profile_pic', read_only=True)
    replies = serializers.SerializerMethodField()
    vote_score = serializers.IntegerField(read_only=True, default=0)
    user_vote = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'article', 'user', 'content', 'parent', 'created_at', 'updated_at',
            'author_username', 'author_profile_pic', 'replies', 'vote_score', 'user_vote'
        ]
        read_only_fields = ['user', 'article']

    def get_replies(self, obj):
        if obj.replies.exists():
            replies = obj.replies.annotate(
                vote_score=Coalesce(Sum('votes__value'), 0)
            ).order_by('-vote_score', '-created_at')
            return CommentSerializer(replies, many=True, context=self.context).data
        return []

    def get_user_vote(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            vote = obj.votes.filter(user=request.user).first()
            return vote.value if vote else 0
        return 0

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['value']


class ArticleListSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source="source.name", read_only=True)
    vote_score = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "url",
            "rss_excerpt",
            "summary",
            "source_name",
            "category",
            "image_url",
            "author",
            "published_at",
            "summary_status",
            "vote_score",
        ]


class ArticleDetailSerializer(serializers.ModelSerializer):
    source = serializers.SerializerMethodField()
    vote_score = serializers.IntegerField(read_only=True, default=0)
    user_vote = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "url",
            "rss_excerpt",
            "content",
            "summary",
            "source",
            "category",
            "image_url",
            "author",
            "published_at",
            "summary_status",
            "summary_error",
            "created_at",
            "updated_at",
            "vote_score",
            "user_vote",
            "comments",
        ]

    def get_comments(self, obj):
        comments = obj.comments.filter(parent__isnull=True).annotate(
            vote_score=Coalesce(Sum('votes__value'), 0)
        ).order_by('-vote_score', '-created_at')
        return CommentSerializer(comments, many=True, context=self.context).data

    def get_source(self, obj):
        return {
            "id": obj.source_id,
            "name": obj.source.name,
            "domain": obj.source.domain,
            "category": obj.source.category,
        }

    def get_user_vote(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            vote = obj.votes.filter(user=request.user).first()
            return vote.value if vote else 0
        return 0
