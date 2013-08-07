from django.db import models
from django.contrib.admin import StackedInline

from forms import MlrmaInlineFormSet

class MlrmaStackedInline(StackedInline):
    formset = MlrmaInlineFormSet
    template = 'admin/mlrma/stackedinline.html'

