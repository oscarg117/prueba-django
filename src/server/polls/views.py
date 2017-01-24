from django.shortcuts import get_object_or_404, render

from django.http import HttpResponseRedirect
#***#
from django.http import HttpResponse    #***#
from django.template import Context     #***#
from django.template.loader import get_template     #***#
from subprocess import Popen, PIPE
import tempfile
import os
#***#
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone

from .models import Choice, Question

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set
        to be published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]

class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Display the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after succesfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results_pdf', args=(question.id,)))


def results_pdf(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    context = {
        'question': question,
    }
    template = get_template('my_latex_template.tex')
    #template = get_template('polls/my_latex_template.tex')
    rendered_tpl = template.render(context).encode('utf-8')
    with tempfile.TemporaryDirectory() as tempdir:
        for i in range(2):
            process = Popen(
                ['pdflatex', '-output-directory', tempdir],
                stdin=PIPE,
                stdout=PIPE,
            )
            process.communicate(rendered_tpl)
        with open(os.path.join(tempdir, 'texput.pdf'), 'rb') as f:
            pdf = f.read()
    r = HttpResponse(content_type='application/pdf')
    #r['Content-Disposition'] = 'attachment; filename=texput.pdf'
    r.write(pdf)
    return r
