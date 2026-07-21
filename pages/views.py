from django.views.generic import TemplateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms import ContactForm

class HomePageView(TemplateView):
    template_name = "home.html"

class AboutPageView(TemplateView):
    template_name = "about.html"



class ContactView(FormView):
    template_name = 'home.html'       # Your template path
    form_class = ContactForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        # Access validated data from form.cleaned_data
        full_name = form.cleaned_data['fullName']
        email = form.cleaned_data['email']
        phone = form.cleaned_data['phone']
        message_text = form.cleaned_data['message']

        # Handle the message (e.g., send an email or log it)
        # send_mail(...)

        # Add success message
        messages.success(self.request, "Your message has been sent successfully!")
        
        return super().form_valid(form)