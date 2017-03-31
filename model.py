from google.appengine.ext import db

class Ad(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    title = db.StringProperty()
    blurb = db.StringProperty(multiline=True)
    price = db.StringProperty()
    price2 = db.IntegerProperty()
    image = db.BlobProperty()
    image_thumb = db.BlobProperty()
    image_medium = db.BlobProperty()
    image_small = db.BlobProperty()
    phone = db.PhoneNumberProperty()
    email = db.EmailProperty()
    billboards = db.ListProperty(db.Key)
    sold = db.BooleanProperty()
    password = db.StringProperty()
    ip = db.StringProperty()

class Billboard(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    title = db.StringProperty()
    phone = db.PhoneNumberProperty()
    email = db.EmailProperty()
    image = db.BlobProperty()
    image_thumb = db.BlobProperty()
    image_medium = db.BlobProperty()
    image_small = db.BlobProperty()
    ads = db.ListProperty(db.Key)
    sponsors = db.ListProperty(db.Key)

class Sponsor(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    title = db.StringProperty()
    image = db.BlobProperty()
