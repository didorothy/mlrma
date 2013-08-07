Multi-Level Related Model Administration
========================================

Multi-Level Related Model Administration for Django enables three levels of 
related Model objects to be edited on a single admin page.

If you have models like the following this tool can help you:

```python
from django.db import models

class A(models.Model):
    title = models.CharField(max_length=100)


class B(models.Model):
    a = models.ForeignKey(A)


class C(models.Model):
    b = models.ForeignKey(B)


class D(models.Model):
    b = models.ForeignKey(B)

```


Usage
=====

In your `admin.py` file (or elsewhere if you organize your code more rigorously) 
you would need something like the following:

```python
from django.contrib import admin
from django.forms.models import modelformset_factory
from mlrma.forms import MlrmaModelForm
from mlrma.models import MlrmaStackedInline

import models

CFormSet = modelformset_factory(models.C, extra=2, can_delete=True, exclude('b',))


class BForm(MlrmaModelForm):
    class Meta:
        model = model.B

    formset_classes = [CFormSet]


class BStackedInline(MlrmaStackedInline):
    model = model.B
    extra = 1
    form = BForm

class AAdmin(admin.ModelAdmin):
    inlines = [BStackedInline]

admin.stie.register(models.A, AAdmin)
```



Notices
=======

Currently code only spot checked to work with Model classes A, B, and C from 
the example above. Theoretically, Model D could also be use (in the same way as 
C) but it has not been tested.

I could use some help creating some unit tests and extending this solution to 
allow for more than 3 levels of relationships. 

Some code taken from core Django 1.5 and modified to meet the needs of this 
project. Per requirements the license for that code is below.

    Copyright (c) Django Software Foundation and individual contributors.
    All rights reserved.
    
    Redistribution and use in source and binary forms, with or without modification,
    are permitted provided that the following conditions are met:
    
        1. Redistributions of source code must retain the above copyright notice, 
           this list of conditions and the following disclaimer.
        
        2. Redistributions in binary form must reproduce the above copyright 
           notice, this list of conditions and the following disclaimer in the
           documentation and/or other materials provided with the distribution.
    
        3. Neither the name of Django nor the names of its contributors may be used
           to endorse or promote products derived from this software without
           specific prior written permission.
    
    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
    ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
    ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
