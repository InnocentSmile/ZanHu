from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods

from notifications.views import notification_handler
from qa.forms import QuestionForm
from zanhu.qa.models import Question, Answer
from zanhu.helpers import AuthorRequireMixin, ajax_required


class QuestionListView(LoginRequiredMixin, ListView):
    """已发布的文章列表"""
    model = Question
    paginate_by = 10
    context_object_name = "questions"
    template_name = 'qa/question_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['popular_tags'] = Question.objects.get_count_tags()
        context["active"] = "all"
        return context


class AnsweredQuestionListView(QuestionListView):
    """已有采纳答案的问题"""

    def get_queryset(self):
        return Question.objects.get_answered()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(AnsweredQuestionListView, self).get_context_data()
        context['popular_tags'] = Question.objects.get_count_tags()
        context["active"] = "answered"
        return context


class UnAnsweredQuestionListView(QuestionListView):
    """已有采纳答案的问题"""

    def get_queryset(self):
        return Question.objects.get_unanswered()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(UnAnsweredQuestionListView, self).get_context_data()
        context['popular_tags'] = Question.objects.get_count_tags()
        context["active"] = "unanswered"
        return context


class QaCreateView(LoginRequiredMixin, CreateView):
    """发表文章"""
    model = Question
    form_class = QuestionForm
    template_name = "qa/question_form.html"
    message = "您的问题已提交!"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """创建成功之后跳转"""
        messages.success(self.request, self.message)
        return reverse_lazy("qa:unanswered_q")


class QaDetailView(LoginRequiredMixin, DetailView):
    """文章详情"""
    model = Question
    context_object_name = "question"
    template_name = 'qa/question_detail.html'


class CreateQuestionView(LoginRequiredMixin, CreateView):
    """回答问题"""
    model = Answer
    fields = ["content", ]
    message = "您的问题已经提交"
    template_name = "qa/answer_form.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.question_id = self.kwargs["question_id"]
        return super(CreateQuestionView, self).form_valid(form)

    def get_success_url(self):
        """创建成功之后跳转"""
        messages.success(self.request, self.message)
        return reverse_lazy("qa:question_detail", kwargs={"pk": self.kwargs["question_id"]})


@login_required
@ajax_required
@require_http_methods(["POST"])
def question_vote(request):
    """给问题投票, AJAX POST请求"""
    question_id = request.POST["question"]
    # U 赞 D 踩
    value = True if request.POST["value"] == 'U' else False
    question = Question.objects.get(pk=question_id)
    # 当前用户的所有投票用户
    users = question.votes.values_list('user', flat=True)

    if request.user.pk in users and (question.votes.get(user=request.user).value == value):
        question.votes.get(user=request.user).delete()
    else:
        question.votes.update_or_create(user=request.user, defaults={"value": value})
    # # 1 用户首次操作, 点赞/踩
    # if request.user.pk not in users:
    #     question.votes.update_or_create(user=request.user, defaults={"value": value})
    # # 2 用户已经赞过,要取消赞/踩一下
    # elif question.votes.get(user=request.user).value:
    #     if value:
    #
    #     else:
    #         question.votes.update_or_create(user=request.user, value=value)
    # # 3 用户已经踩过,取消踩/赞一下
    # else:
    #     if not value:
    #         question.votes.get(user=request.user).delete()
    #     else:
    #         question.votes.update_or_create(user=request.user, value=value)
    return JsonResponse({"votes": question.total_votes()})


@login_required
@ajax_required
@require_http_methods(["POST"])
def answer_vote(request):
    """给问题投票, AJAX POST请求"""
    answer_id = request.POST["answer"]
    # U 赞 D 踩
    value = True if request.POST["value"] == 'U' else False
    answer = Answer.objects.get(uuid_id=answer_id)
    # 当前用户的所有投票用户
    users = answer.votes.values_list('user', flat=True)

    if request.user.pk in users and (answer.votes.get(user=request.user).value == value):
        answer.votes.get(user=request.user).delete()
    else:
        answer.votes.update_or_create(user=request.user, defaults={"value": value})
    return JsonResponse({"votes": answer.total_votes()})


@login_required
@ajax_required
@require_http_methods(["POST"])
def accept_answer(request):
    """接受回答 AJAX POST 请求 已经接受的回答不能取消"""
    answer_id = request.POST["answer"]
    answer = Answer.objects.get(uuid_id=answer_id)
    # 如果当前登录用户不是提问者,跑出权限拒绝错误
    if answer.question.user.username != request.user.username:
        raise PermissionDenied
    answer.accept_answer()
    # 通知回答者
    notification_handler(request.user, answer.user, 'W', answer)
    return JsonResponse({"status": "true"})
