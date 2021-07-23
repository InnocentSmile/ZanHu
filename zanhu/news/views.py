from django.db.models import F
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render

from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DeleteView
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.urls import reverse_lazy

from helpers import ajax_required, AuthorRequireMixin
from zanhu.news.models import News


class NewsListView(LoginRequiredMixin, ListView):
    '''首页动态'''
    model = News
    # queryset = News.objects.all()
    paginate_by = 20  # url中的?page=
    # page_kwarg = "p"
    # context_object_name = "news_list" # 默认值是'模型类名_list'或者'object_list'
    # ordering = 'created_at' # 多个字段排序('x', 'y',  )
    template_name = 'news/news_list.html'  # 默认是 模型名_list.html

    # def get_ordering(self):
    #     '''个性排序, 自定义排序'''
    #     pass
    #
    # def get_paginate_by(self, queryset):
    #     '''自定义分页'''
    #     pass
    #
    def get_queryset(self):
        return News.objects.filter(reply=False)
    #
    # def get_context_data(self, *, object_list=None, **kwargs):
    #     '''添加额外的上下文'''
    #     context = super().get_context_data()
    #     context['views'] = 100
    #     return context


class NewsDeleteView(LoginRequiredMixin, AuthorRequireMixin, DeleteView):
    model = News
    # template_name = "news/news_confirm_delete.html"
    # slug_url_kwarg = 'slug' # 通过url传入要删除的对象的主键id 默认值是slug
    # pk_url_kwarg = 'pk'  # 通过url传入要删除的对象的主键id 默认值是slug
    success_url = reverse_lazy("news:list")  # 在项目URLConf未加载前使用


@login_required
@ajax_required
@require_http_methods(["POST"])
def post_new(request):
    """发送动态,AJAX POST请求"""
    post = request.POST["post"].strip()
    if post:
        posted = News.objects.create(user=request.user, content=post)
        html = render_to_string("news/news_single.html", {'news': posted, 'request': request})
        return HttpResponse(html)
    else:
        return HttpResponseBadRequest("内容不能为空")


@login_required
@ajax_required
@require_http_methods(["POST"])
def like(request):
    """点赞,AJAX POST请求"""
    news_id = request.POST['news']
    news = News.objects.get(pk=news_id)
    news.switch_like(request.user)
    return JsonResponse({"likes": news.count_likers()})


@login_required
@ajax_required
@require_http_methods(["GET"])
def get_thread(request):
    """返回动态的评论,AJAX GET请求"""
    news_id = request.GET['news']
    news = News.objects.get(pk=news_id)
    news_html = render_to_string('news/news_single.html', {'news': news})
    thread_html = render_to_string('news/news_thread.html', {"thread": news.get_thread()})
    return JsonResponse({
        "uuid": news_id,
        "news": news_html,
        "thread": thread_html,
    })


@login_required
@ajax_required
@require_http_methods(["POST"])
def post_comment(request):
    """评论,AJAX GET请求"""
    post = request.POST['reply'].strip()
    parent_id = request.POST['parent']
    parent = News.objects.get(pk=parent_id)
    if post:
        parent.reply_this(request.user, post)
        return JsonResponse({'comments': parent.comment_count()})
    else:
        return HttpResponseBadRequest("内容不能为空")


@csrf_exempt
def sub_nums(request):
    import time
    # import random
    # time.sleep(random.randint(0,5))
    post = request.GET['post'].strip()
    news = News.objects.get(pk=post)
    news.nums = F('nums') - 1
    # news.nums -= 1
    news.save()
    return HttpResponse("ok")


@login_required
@ajax_required
@require_http_methods(["POST"])
def update_interactions(request):
    """更新互动信息"""
    data_point = request.POST['id_value']
    news = News.objects.get(pk=data_point)
    return JsonResponse({'likes': news.count_likers(), 'comments': news.comment_count()})
