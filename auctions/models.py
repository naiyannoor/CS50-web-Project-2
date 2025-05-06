from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE, DO_NOTHING
from datetime import datetime

class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', blank=True, related_name="watchlists")
    pass

class Category(models.Model):
    category = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.category}"

class Listing(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=2500)
    image_url = models.URLField(blank=True)
    user = models.ForeignKey(User, on_delete=CASCADE, related_name="listings")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="listings")
    time_created = models.DateTimeField(auto_now=True)
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE, related_name="bids")
    price = models.DecimalField(decimal_places=2, max_digits=10)
    listing = models.OneToOneField(Listing, on_delete=CASCADE, related_name="bids")
    num_of_bids = models.IntegerField(default=1, editable=False)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            orig = Bid.objects.get(pk=self.pk)
            if self.price != orig.price:
                self.num_of_bids=self.num_of_bids+1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"${self.price}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=DO_NOTHING, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=CASCADE, related_name="comments")
    content = models.CharField(max_length=2000)
    time_commented = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.time_commented=datetime.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.listing} - {self.user}: {self.content}"