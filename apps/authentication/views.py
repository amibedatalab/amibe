import logging

from django.shortcuts import render, redirect, reverse
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.conf import settings

from apps.authentication.forms import CustomAuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.views import PasswordResetView
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail.backends.smtp import EmailBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages


logger = logging.getLogger(__name__)


class HomeView(LoginRequiredMixin, View):
    class_name = 'HomeView'
    login_url = '/hub/login/'

    def get(self, request):
        logger.info(f'{self.class_name}_get :: user :: {request.user}')
        return render(request, 'home/home.html')


class LogoutView(View):
    class_name = 'LogoutView'

    def get(self, request):
        logger.info(f'{self.class_name}_get:: user {request.user} logout.')
        logout(request)
        return redirect(reverse('login'))


class SigninView(View):
    class_name = 'SigninView'

    def get(self, request):
        logger.info(f'{self.class_name}_get called..')
        form = CustomAuthenticationForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = CustomAuthenticationForm(data=request.POST)

        if form.is_valid():
            email = form.cleaned_data['username']  # Use 'username' as the email input
            password = form.cleaned_data['password']

            user = authenticate(request, email=email, password=password)  # Authenticate by email
            if user is not None:
                login(request, user)
                logger.info(f'{self.class_name}_post:: user {user} login.')
                return redirect(reverse('home'))

        return render(request, 'login.html', context={'form': form})


class CustomPasswordChangeView(PasswordChangeView):
    # redirect urs to login whenever password changed
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        # Perform the default password change behavior
        response = super().form_valid(form)

        # TODO:: Send mail wheneven password changed.

        # Log out the user
        logout(self.request)

        return response


class CustomPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        # Process the form and send the reset email
        return redirect(reverse('password_reset_done'))
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email', None)
        if not email:
            # Handle the case where email is not provided
            messages.error(
                request,
                "Please enter your email address."
            )
            return self.render_to_response(self.get_context_data())
        try:
            user = get_user_model().objects.get(email=email)
        except ObjectDoesNotExist:
            if email.endswith('@canarahsbclife.in'):
                messages.error(
                    request,
                    settings.INVALID_EMAIL_ERROR
                )
            else:
                messages.error(
                    request,
                    settings.INVALID_EMAIL_ADDRESS
                )
            return self.render_to_response(self.get_context_data())

        # user = get_user_model().objects.get(email=email)
        # uid = urlsafe_base64_encode(force_bytes(user.pk))
        # token = default_token_generator.make_token(user)
        # reset_url = f'http://13.233.156.126/hub/password-reset-confirm/{uid}/{token}/'
        # from_email = 'noreply.automationhub@canarahsbclife.in'
        # backend = EmailBackend(
        #      host='smtp.netud.net',
        #     port='587',
        #     username='rpa1',
        #     password='Canara@15',
        #     use_tls=True,
        #     fail_silently=False
        # )
        # msg = EmailMessage(
        #     subject='reset request',
        #     body=f"Dear User,\n\nYou can reset your password by clicking the following link:\n{reset_url}\n\nIf you did not request this password reset, please ignore this email.",
        #    from_email=f'Support Automation Hub <{from_email}>',
        #     to=[email],
        #     connection=backend
        # )
        # msg.send(fail_silently=False)
        return super().post(request, *args, **kwargs)
