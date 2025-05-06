from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate, login, logout
from django.db import IntegrityError
from django.forms import widgets
from django.forms.widgets import NumberInput, Select, TextInput, Textarea, URLInput, Widget
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from .models import User, Listing, Bid, Comment, Category

class CreateForm(forms.Form):
    title = forms.CharField(widget=TextInput(attrs={'class': 'create_form', 'placeholder': 'Title', 'maxlength': 200}), label='')
    description = forms.CharField(widget=Textarea(attrs={'class': 'create_form', 'placeholder': 'Description', 'maxlength': 2500}), label='')
    image_url = forms.URLField(widget=URLInput(attrs={'class': 'create_form', 'placeholder': 'Image URL (optional)'}), required=False, label='')
    price = forms.DecimalField(widget=NumberInput(attrs={'class': 'create_form', 'placeholder': 'Starting Bid'}), min_value=1, label='')
    category = forms.ModelChoiceField(widget=Select(attrs={'class': 'create_form choice'}), queryset=Category.objects.all(), required=False)
    add_category = forms.CharField(widget=TextInput(attrs={'class': 'create_form', 'placeholder': 'Add New Category if product category is not in the list (optional)', 'maxlength': 200}), required=False, label='')

class CommentForm(forms.Form):
    comment = forms.CharField(widget=TextInput(attrs={'class': 'create_form', 'placeholder': 'Add a comment', 'maxlength':2000}), label='', required=False)

def index(request):
    listings=Listing.objects.all()
    if request.user.is_authenticated:
        current_user = User.objects.get(username=request.user)
        user_watchlist = current_user.watchlist.all()
        return render(request, "auctions/index.html", {
            "listings": listings.order_by('title'),
            "category_names": Category.objects.all().order_by('category'),
            "user_watchlist":user_watchlist
        })
    return render(request, "auctions/index.html", {
        "listings": listings.order_by('title'),
        "category_names": Category.objects.all().order_by('category'),
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def listing(request, listing_id):
    if request.user.is_authenticated:
        current_price = Bid.objects.get(listing=listing_id)
        current_price = current_price.price
        current_user = User.objects.get(username=request.user)
        user_watchlist = current_user.watchlist.all()
        if request.method == 'POST':
            if request.POST.__contains__('comment'):
                com = CommentForm(request.POST)
                if com.is_valid():
                    new_comment = com.cleaned_data['comment']
                    new_comment = Comment(user=request.user, listing=Listing.objects.get(id=listing_id), content=new_comment)
                    new_comment.save()
                    bids = Bid.objects.get(listing=listing_id)
                    return render(request, "auctions/listing.html", {
                        "listing": Listing.objects.get(id=listing_id),
                        "bid": bids,
                        "user": request.user,
                        "category_names": Category.objects.all().order_by('category'),
                        "comments": Comment.objects.filter(listing=listing_id).order_by('-time_commented'),
                        "comment_form":CommentForm(),
                        "user_watchlist":user_watchlist
                    })
            else:
                new_price = request.POST['price']
                if int(new_price)<=current_price:
                    bids = Bid.objects.get(listing=listing_id)
                    return render(request, "auctions/listing.html", {
                    "listing": Listing.objects.get(id=listing_id),
                    "bid": bids,
                    "user": request.user,
                    "error_msg": "Your bid must be higher than the current bid!",
                    "category_names": Category.objects.all().order_by('category'),
                    "comments": Comment.objects.filter(listing=listing_id).order_by('-time_commented'),
                    "comment_form":CommentForm(),
                    "user_watchlist":user_watchlist
                })
                else:
                    new_bid=Bid.objects.get(listing=listing_id)
                    new_bid.price=new_price
                    new_bid.user=request.user
                    new_bid.save()
                    bids = Bid.objects.get(listing=listing_id)
                    return render(request, "auctions/listing.html", {
                    "listing": Listing.objects.get(id=listing_id),
                    "bid": bids,
                    "user": request.user,
                    "success_msg": "Your bid has successfully been placed!",
                    "category_names": Category.objects.all().order_by('category'),
                    "comments": Comment.objects.filter(listing=listing_id).order_by('-time_commented'),
                    "comment_form":CommentForm(),
                    "user_watchlist":user_watchlist
                })
        else:
            bids = Bid.objects.get(listing=listing_id)
            return render(request, "auctions/listing.html", {
                "listing": Listing.objects.get(id=listing_id),
                "bid": bids,
                "user": request.user,
                "category_names": Category.objects.all().order_by('category'),
                "comments": Comment.objects.filter(listing=listing_id).order_by('-time_commented'),
                "comment_form":CommentForm(),
                "user_watchlist":user_watchlist
            })
    else:
        bids = Bid.objects.get(listing=listing_id)
        return render(request, "auctions/listing.html", {
            "listing": Listing.objects.get(id=listing_id),
            "bid": bids,
            "user": request.user,
            "category_names": Category.objects.all().order_by('category'),
            "comments": Comment.objects.filter(listing=listing_id).order_by('-time_commented'),
            "comment_form":CommentForm(),   
        })

@login_required(login_url='login')
def category(request, category_name):
    if category_name=='noCat':
        ls = Listing.objects.filter(category__isnull=True).order_by('title')
        current_user = User.objects.get(username=request.user)
        user_watchlist = current_user.watchlist.all()
        return render(request, "auctions/category.html", {
            "listings":ls,
            "category_names": Category.objects.all().order_by('category'),
            "category":"No Category",
            "user_watchlist":user_watchlist
        })
    cg = Category.objects.get(category=category_name)
    ls = Listing.objects.filter(category=cg.id).order_by('title')
    current_user = User.objects.get(username=request.user)
    user_watchlist = current_user.watchlist.all()
    return render(request, "auctions/category.html", {
        "listings":ls,
        "category_names": Category.objects.all().order_by('category'),
        "category":category_name,
        "user_watchlist":user_watchlist
    })

@login_required(login_url='login')
def watchlist(request):
    current_user = User.objects.get(username=request.user)
    user_watchlist = current_user.watchlist.all()
    return render(request, 'auctions/watchlist.html', {
        "watchlist":user_watchlist.order_by('title'),
        "category_names": Category.objects.all().order_by('category'),
        "user_watchlist":user_watchlist
    })

@login_required(login_url='login')
def create(request):
    if request.method != 'POST':
        return render(request, 'auctions/create.html', {
            "CreateForm": CreateForm(),
            "category_names": Category.objects.all().order_by('category'),
        })
    else:
        form = CreateForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            image_url = form.cleaned_data['image_url']
            starting_price = form.cleaned_data['price']
            category = form.cleaned_data['category']
            add_category = form.cleaned_data['add_category']
            if(category and add_category):
                return render(request, 'auctions/create.html', {
                "CreateForm": CreateForm(),
                "error_msg": "Please fill in maximum (1) category field only!",
                "category_names": Category.objects.all().order_by('category')
                })
            elif(add_category):
                if(Category.objects.filter(category=add_category).exists()):
                    return render(request, 'auctions/create.html', {
                    "CreateForm": CreateForm(),
                    "error_msg": "New category cannot be similar to provided category field!",
                    "category_names": Category.objects.all().order_by('category')
                    })
                c = Category.objects.create(category=add_category)
                new_listing = Listing.objects.create(title=title, description=description, image_url=image_url, category=c, user=request.user)
                Bid.objects.create(listing=new_listing, user=request.user, price=starting_price)
                return render(request, 'auctions/create.html', {
                "CreateForm": CreateForm(),
                "success_msg": "Listing Successfully Added!",
                "category_names": Category.objects.all().order_by('category')
                })
            else:
                new_listing = Listing.objects.create(title=title, description=description, image_url=image_url, category=category, user=request.user)
                Bid.objects.create(listing=new_listing, user=request.user, price=starting_price)
                return render(request, 'auctions/create.html', {
                "CreateForm": CreateForm(),
                "success_msg": "Listing Successfully Added!",
                "category_names": Category.objects.all().order_by('category')
                })

@login_required(login_url='login')
def edit(request, listing_id):
    current_user = User.objects.get(username=request.user)
    listing = Listing.objects.get(id = listing_id)
    if listing in current_user.watchlist.all():
        current_user.watchlist.remove(listing)
    else:
        current_user.watchlist.add(listing)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='login')
def close(request, listing_id):
    listing = Listing.objects.get(id = listing_id)
    listing.is_open=False
    listing.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='login')
def myListings(request):
    ls = Listing.objects.filter(user=request.user).order_by("title")
    current_user = User.objects.get(username=request.user)
    user_watchlist = current_user.watchlist.all()
    return render(request, "auctions/mylistings.html", {
        "listings":ls,
        "category_names": Category.objects.all().order_by('category'),
        "user_watchlist":user_watchlist
    })