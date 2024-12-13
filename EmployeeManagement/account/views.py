from django.shortcuts import render, get_object_or_404, redirect
from .models import Form, DynamicField,FormFieldSubmission
from django import forms
from django.urls import reverse_lazy
from django.views.generic import ListView,View,CreateView,TemplateView
from .forms import DynamicfieldValue,LoginForm,UserForm,ChangePasswordForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password

def signin_requered(fn):

    def wrapper(request,*args,**kw):
        if not request.user.is_authenticated:

            messages.error(request,'you must login')
            return redirect('login')
        
        else:
            return fn(request,*args,**kw)
        
    return wrapper


@method_decorator(signin_requered,name='dispatch') 
class Homeview(ListView):
    
    template_name='home.html'
    model=Form
    context_object_name='item'

    def get_queryset(self):
        
        return Form.objects.filter(user=self.request.user)


@signin_requered 
def create_form_view(request):
    if request.method == 'POST':
        user = request.user
        form_name = request.POST.get('form_name')
        new_form = Form.objects.create(name=form_name,user=user)

        field_counter = 1
        while f'label_{field_counter}' in request.POST:
            label = request.POST.get(f'label_{field_counter}')
            field_type = request.POST.get(f'field_type_{field_counter}')
            DynamicField.objects.create(form=new_form, label=label, field_type=field_type)
            field_counter += 1

        return render(request, 'dynamic_form.html', {'message': 'Form and fields added successfully!'})

    return render(request, 'dynamic_form.html')


def view_dynamic_form(request, form_id):
    user=request.user
    form_instance = get_object_or_404(Form, id=form_id,user=user)
    
   
    dynamic_fields = DynamicField.objects.filter(form=form_instance)
    
  
    dynamic_form_fields = {}

    for field in dynamic_fields:
        if field.field_type == 'text':
            dynamic_form_fields[field.label] = forms.CharField(label=field.label)
        elif field.field_type == 'number':
            dynamic_form_fields[field.label] = forms.IntegerField(label=field.label)
        elif field.field_type == 'date':
            dynamic_form_fields[field.label] = forms.DateTimeField(label=field.label)
        elif field.field_type == 'password':
            dynamic_form_fields[field.label] = forms.CharField(widget=forms.PasswordInput(), label=field.label)

  
    DynamicForm = type('DynamicForm', (forms.Form,), dynamic_form_fields)


    if request.method == 'POST':
      
        form = DynamicForm(request.POST)
        form_response_table=FormFieldSubmission.objects.all().last()
        count=0
        if form_response_table:
            unique_id=form_response_table.unique_id
            if unique_id is not None:
                
                count=unique_id+1
            else:
                count=1
        else:
            count=1
        
        if form.is_valid():
            
            try:
                for field, value in form.cleaned_data.items():
                    FormFieldSubmission.objects.create(
                        form=form_instance,  
                        field_label=field,
                        field_value=value,
                        unique_id=count
                    )

              
                return render(request, 'view_dynamic_form.html', {
                    'form': form,
                    'message': 'Form submitted successfully!'
                })
            except Exception as e:
               
                return render(request, 'view_dynamic_form.html', {
                    'form': form,
                    'message': f'Error while saving form: {str(e)}'
                })
        else:
            return render(request, 'view_dynamic_form.html', {
                'form': form,
                'message': 'Please correct the errors below.'
            })

    
    return render(request, 'view_dynamic_form.html', {'form': DynamicForm()})


class FormResponses(View):
    
    def get(self,request,*args,**kw):
        id=kw.get('id')
  
        form_responses = DynamicField.objects.filter(form_id=id)
        formtable = FormFieldSubmission.objects.filter(form_id=id)

        count=form_responses.count()
        labels = [response.label for response in form_responses]
        label_values = [response.field_value for response in formtable]
        unique_id=[response.unique_id for response in formtable]

       
        count = form_responses.count()

        grouped_data=[label_values[i:i+count] for i in range(0,len(label_values),count)]
        result=[dict(zip(labels,values)) for values in grouped_data]
        unique_number = sorted(set(unique_id)) 
        result = [{"id": unique_id, **item} for unique_id, item in zip(unique_number, result)]


     
        return render(request, 'submitted_data.html', {'form_id': id, 'results': result})
    

class Deletedata(View):
    def post(self, request, *args, **kwargs):
        if request.POST.get('_method') == 'DELETE':
            id=kwargs.get('id')
            form_id=kwargs.get('form_id')
            table_data=FormFieldSubmission.objects.filter(unique_id=id)
            table_data.delete()
            return redirect('form_responses',id=form_id)
        
class FieldUpdate(View):
    def get(self, request, form_id, unique_id):
   
        form_submission = FormFieldSubmission.objects.filter(unique_id=unique_id, form_id=form_id)
        
    
        form_responses = DynamicField.objects.filter(form_id=form_id)


        forms = []
        for submission in form_submission:

            form = DynamicfieldValue(instance=submission) 
            forms.append(form)

        return render(request, 'update_field.html', {
            'forms': forms,
            'form_submission': form_submission,
            'form_responses': form_responses,
            'form_id': form_id,
            'unique_id': unique_id
        })
    def post(self, request, form_id, unique_id):
   
        form_submissions = FormFieldSubmission.objects.filter(unique_id=unique_id, form_id=form_id)

    
        form_responses = DynamicField.objects.filter(form_id=form_id)

        forms = []
        if form_submissions.exists():
            for submission in form_submissions:
               
                form = DynamicfieldValue(request.POST, instance=submission)
                forms.append(form)

            submitted_form_id = request.POST.get('form_id')
            

            form_to_update = next((form for form in forms if form.instance.id == int(submitted_form_id)), None)

            if form_to_update and form_to_update.is_valid():
                form_to_update.save()  
                return redirect('form_responses', id=form_id)  

        
        return render(request, 'update_field.html', {
            'forms': forms,
            'form_responses': form_responses,
            'form_id': form_id,
            'unique_id': unique_id
        })
    

class UserCreationView(CreateView):
    template_name='register.html'
    form_class=UserForm
    success_url=reverse_lazy('login')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password!")
            return redirect("login")

    return render(request, "login.html")



def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("login")



class PasswordChangeView(View):
    template_name = 'change_password.html'

    def get(self, request, *args, **kwargs):
       
        form = ChangePasswordForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = ChangePasswordForm(request.POST)
        
        if form.is_valid():
            user = request.user
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']

           
            if not check_password(old_password, user.password):
                form.add_error('old_password', 'Old password is incorrect.')
                return render(request, self.template_name, {'form': form})

            
            user.set_password(new_password)
            user.save()

           
            update_session_auth_hash(request, user)

            return redirect("home")

       
        return render(request, self.template_name, {'form': form})
    
class Accountsection(TemplateView):
    template_name='account.html'