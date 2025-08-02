from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import UserProfile, Invite
from .forms import RegistrationForm, CompanyRegistrationForm, ProfilePictureForm
from projects.models import Task


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        context = {'form': form}
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return render(request, 'register/reg_form.html', {'created': True})
        return render(request, 'register/reg_form.html', context)
    else:
        return render(request, 'register/reg_form.html', {'form': RegistrationForm()})


def usersView(request):
    users = UserProfile.objects.all()
    tasks = Task.objects.all()
    return render(request, 'register/users.html', {'users': users, 'tasks': tasks})


def user_view(request, profile_id):
    user = UserProfile.objects.get(id=profile_id)
    return render(request, 'register/user.html', {'user_view': user})


def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    logged_user = get_active_profile(request)

    if request.method == 'POST':
        img_form = ProfilePictureForm(request.POST, request.FILES, instance=logged_user)
        if img_form.is_valid():
            img_form.save()
            return render(request, 'register/profile.html', {
                'img_form': img_form,
                'updated': True,
                'logged_user': logged_user,
            })
        return render(request, 'register/profile.html', {
            'img_form': img_form,
            'logged_user': logged_user
        })
    else:
        img_form = ProfilePictureForm(instance=logged_user)
        return render(request, 'register/profile.html', {
            'img_form': img_form,
            'logged_user': logged_user
        })


def newCompany(request):
    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'register/new_company.html', {
                'created': True,
                'form': CompanyRegistrationForm()
            })
        return render(request, 'register/new_company.html', {'form': form})
    else:
        return render(request, 'register/new_company.html', {'form': CompanyRegistrationForm()})


def invites(request):
    return render(request, 'register/invites.html')


def invite(request, profile_id):
    profile_to_invite = UserProfile.objects.get(id=profile_id)
    logged_profile = get_active_profile(request)
    if profile_to_invite not in logged_profile.friends.all():
        logged_profile.invite(profile_to_invite)
    return redirect('core:index')


def deleteInvite(request, invite_id):
    logged_user = get_active_profile(request)
    logged_user.received_invites.get(id=invite_id).delete()
    return render(request, 'register/invites.html')


def acceptInvite(request, invite_id):
    invite = Invite.objects.get(id=invite_id)
    invite.accept()
    return redirect('register:invites')


def remove_friend(request, profile_id):
    user = get_active_profile(request)
    user.remove_friend(profile_id)
    return redirect('register:friends')


def get_active_profile(request):
    return request.user.userprofile


def friends(request):
    if request.user.is_authenticated:
        user = get_active_profile(request)
        friends = user.friends.all()
        return render(request, 'register/friends.html', {'friends': friends})
    else:
        users_prof = UserProfile.objects.all()
        return render(request, 'register/friends.html', {'users_prof': users_prof})
