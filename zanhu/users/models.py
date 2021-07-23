from __future__ import unicode_literals

from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


@python_2_unicode_compatible
class User(AbstractUser):
    """自定义用户模型"""
    nickname = models.CharField("昵称", max_length=255, null=True, blank=True)
    job_title = models.CharField("职称", max_length=50, null=True, blank=True)
    introduction = models.TextField("简介", blank=True, null=True)
    picture = models.ImageField("头像", upload_to='profile_pics/', null=True, blank=True)
    location = models.CharField("城市", max_length=50, null=True, blank=True)
    personal_url = models.CharField("个人链接", max_length=255, null=True, blank=True)
    weibo = models.CharField("微博链接", max_length=255, null=True, blank=True)
    zhihu = models.CharField("知乎链接", max_length=255, null=True, blank=True)
    github = models.CharField("GitHub链接", max_length=255, null=True, blank=True)
    linkedin = models.CharField("LinkedIn链接", max_length=255, null=True, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    def get_profile_name(self):
        if self.nickname:
            return self.nickname
        return self.username
