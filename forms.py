from django.forms.models import BaseInlineFormSet, modelformset_factory, ModelForm

def find_fk(to_search, to_find):
    '''Takes two model objects and finds the field in to_search that is a FK to to_find.
    
    If no FK field is found then returns None. If more than one, only the first one found is returned.
    '''
    for field in to_search._meta.fields:
        if field.get_internal_type() == 'ForeignKey':
            if field.rel.to == to_find:
                return field
    return None


class MlrmaModelForm(ModelForm):
    '''Represents a form that has multiple formsets for related items.'''
    
    # the formsets that are related to the Model this form represents
    formset_classes = []
    
    # custom field to use for the foreign key of a specific formset as set in self.formset_classes
    formset_class_fk_fields = {}
    
    def get_fk_field(self, formset_class):
        '''Retrieves, either by lookup or searching, the FK field of the passed in FormSet class.'''
        if formset_class in self.formset_class_fk_fields:
            return self.formset_class_fk_fields[formset_class]
        else:
            return find_fk(formset_class.model, self._meta.model)
    
    def __init__(self, **kwargs):
        super(MlrmaModelForm, self).__init__(**kwargs)
        
        self.formsets = []
        for cls in self.formset_classes:
            fk_field = self.get_fk_field(cls)
            formset = cls(queryset=cls.model.objects.filter(**{fk_field.name: self.instance}), data=self.data or None, files=self.files or None, prefix=self.prefix or None)
            formset.opts = formset.model._meta
            self.formsets.append(formset)
    
    def is_valid(self):
        is_valid = True
        for formset in self.formsets:
            # ensure that is_valid is called on all nested formsets.
            if not formset.is_valid():
                is_valid = False
                
        return (super(MlrmaModelForm, self).is_valid() and is_valid)
    
    def has_changed(self):
        has_changed = False
        for formset in self.formsets:
            if formset.has_changed():
                has_changed = True
        return (super(MlrmaModelForm, self).has_changed() or has_changed)
    
    def save(self, commit=True):
        res = super(MlrmaModelForm, self).save(commit=commit)
        nested_objects = []
        for formset in self.formsets:
            objs = formset.save(commit=False)
            for obj in objs:
                fk_field = self.get_fk_field(formset.__class__)
                nested_objects.append((obj, fk_field))
                if commit:
                    setattr(obj, fk_field.name, self.instance)
                    obj.save()
        return [res, nested_objects]


class MlrmaInlineFormSet(BaseInlineFormSet):
    '''A formset containing one or more MlrmaModelForm.'''
    
    def save_existing_objects(self, commit=True):
        self.changed_objects = []
        self.deleted_objects = []
        if not self.initial_forms:
            return []

        saved_instances = []
        try:
            forms_to_delete = self.deleted_forms
        except AttributeError:
            forms_to_delete = []
        for form in self.initial_forms:
            pk_name = self._pk_field.name
            raw_pk_value = form._raw_value(pk_name)

            # clean() for different types of PK fields can sometimes return
            # the model instance, and sometimes the PK. Handle either.
            pk_value = form.fields[pk_name].clean(raw_pk_value)
            pk_value = getattr(pk_value, 'pk', pk_value)

            obj = self._existing_object(pk_value)
            if form in forms_to_delete:
                self.deleted_objects.append(obj)
                obj.delete()
                continue
            if form.has_changed():
                self.changed_objects.append((obj, form.changed_data))
                tmp_instance = self.save_existing(form, obj, commit=commit)
                if isinstance(tmp_instance, list):
                    for inst in tmp_instance:
                        saved_instances.append(inst)
                else:
                    saved_instances.append(tmp_instance)
                if not commit:
                    self.saved_forms.append(form)
        return saved_instances

    def save_new_objects(self, commit=True):
        self.new_objects = []
        for form in self.extra_forms:
            if not form.has_changed():
                continue
            # If someone has marked an add form for deletion, don't save the
            # object.
            if self.can_delete and self._should_delete_form(form):
                continue
            tmp_obj = self.save_new(form, commit=commit)
            if isinstance(tmp_obj, list):
                for o in tmp_obj:
                    self.new_objects.append(o)
            else:
                self.new_objects.append(tmp_obj)
            if not commit:
                self.saved_forms.append(form)
        return self.new_objects
    
    def save_new(self, form, commit=True):
        # Use commit=False so we can assign the parent key afterwards, then
        # save the object.
        obj = form.save(commit=False)
        pk_value = getattr(self.instance, self.fk.rel.field_name)
        if isinstance(obj, list):
            setattr(obj[0], self.fk.get_attname(), getattr(pk_value, 'pk', pk_value))
        else:
            setattr(obj, self.fk.get_attname(), getattr(pk_value, 'pk', pk_value))
        if commit:
            if isinstance(obj, list):
                obj[0].save()
                for o in obj[1]:
                    print o[0], o[1], obj[0].id
                    setattr(o[0], o[1].name, obj[0])
                    o[0].save()
            else:
                obj.save()
        # form.save_m2m() can be called via the formset later on if commit=False
        if commit and hasattr(form, 'save_m2m'):
            form.save_m2m()
        return obj

