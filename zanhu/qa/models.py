import uuid
from collections import Counter

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from slugify import slugify
from taggit.managers import TaggableManager
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey


@python_2_unicode_compatible
class Vote(models.Model):
    """使用Django的ContentType, 同时关联用户对问题和回答的投票"""
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="qa_vote",
                             verbose_name="用户")
    value = models.BooleanField(default=True, verbose_name="赞同或者反对")  # True赞同
    content_type = models.ForeignKey(ContentType, related_name="votes_on", on_delete=models.CASCADE)
    object_id = models.CharField("", max_length=255)
    vote = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "投票"
        verbose_name_plural = verbose_name
        unique_together = ('user', 'content_type', 'object_id')
        # SQL优化
        index_together = ('content_type', 'object_id')


@python_2_unicode_compatible
class QuestionQuerySet(models.query.QuerySet):
    """自定义QuerySet, 提高模型类的可用性"""

    def get_answered(self):
        """已有答案的问题"""
        return self.filter(has_answer=True)

    def get_unanswered(self):
        "未被回答的问题"
        return self.filter(has_answer=False)

    def get_count_tags(self):
        """统计所有问题标签的数量(大于0的)"""
        tag_dict = {}
        query = self.all()
        for obj in query:
            for tag in obj.tags.names():
                if tag not in tag_dict:
                    tag_dict[tag] = 1
                else:
                    tag_dict[tag] += 1
        return tag_dict.items()


@python_2_unicode_compatible
class Question(models.Model):
    STATUS = (
        ("O", "Open"),
        ("C", "Close"),
        ("D", "Draft"),

    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="q_author",
                             verbose_name="提问者")
    title = models.CharField("标题", unique=True, max_length=255)
    slug = models.SlugField("(URL)别名", max_length=255)
    status = models.CharField("状态", max_length=1, choices=STATUS, default="O")
    content = MarkdownxField("内容")
    tags = TaggableManager("标签", help_text="多个标签使用,(英文)隔开")
    has_answer = models.BooleanField("接受回答", default=False)
    votes = GenericRelation(Vote, verbose_name="投票情况")  # 通过GenericRelation关联到vote 并不是实际字段
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    objects = QuestionQuerySet.as_manager()

    class Meta:
        verbose_name = "问题"
        verbose_name_plural = "问题"
        ordering = ("created_at",)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Question, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_markdown(self):
        """将markdown文本转换成HTML"""
        return markdownify(self.content)

    def total_votes(self):
        """得票数"""
        dic = Counter(self.votes.values_list('value', flat=True))
        return dic[True] - dic[False]

    def count_answers(self):
        """回答数量"""
        return self.get_answers().count()

    def get_answers(self):
        """获取所有回答"""
        return Answer.objects.filter(question=self)

    def get_upvoters(self):
        """赞同的用户"""
        return [vote.user for vote in self.votes.filter(value=True)]

    def get_downvoters(self):
        """踩的用户"""
        return [vote.user for vote in self.votes.filter(value=False)]

    def get_accepted_answer(self):
        """被接受的回答"""
        return Answer.objects.get(question=self, is_answer=True)


@python_2_unicode_compatible
class Answer(models.Model):
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="a_author",
                             verbose_name="回答者")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = MarkdownxField("内容")
    is_answer = models.BooleanField("回答是否被接受", default=False)
    votes = GenericRelation(Vote, verbose_name="投票情况")  # 通过GenericRelation关联到vote 并不是实际字段
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "回答"
        verbose_name_plural = "回答"
        ordering = ("-is_answer", "-created_at")

    def __str__(self):
        return self.content[:20]

    def get_markdown(self):
        """将markdown文本转换成HTML"""
        return markdownify(self.content)

    def total_votes(self):
        """得票数"""
        dic = Counter(self.votes.values_list('value', flat=True))
        return dic[True] - dic[False]

    def get_downvoters(self):
        """踩的用户"""
        return [vote.user for vote in self.votes.filter(value=False)]

    def get_accepted_answer(self):
        """被接受的回答"""
        return Answer.objects.get(question=self, is_answer=True)

    def accept_answer(self):
        """接受回答"""
        # 当一个问题有多个回答的时候,只能采纳一个回答 其他回答一律置位未接受
        answer_set = Answer.objects.filter(question=self.question)
        answer_set.update(is_answer=False)
        self.is_answer = True
        self.save()
        self.question.has_answer = True
        self.question.save()
