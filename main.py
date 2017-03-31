import os.path
import hashlib
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.api import images
from django.utils import simplejson
from model import Ad
from model import Billboard
from model import Sponsor
from config import SALT
from config import GOOGLE_ANALYTICS_ACCOUNT

class MainHandler(webapp.RequestHandler):
    def get(self):
        args = {
            'ads': Ad.all().order('-created').fetch(100),
            'billboards': Billboard.all().order('-created').fetch(100),
            'body_id': 'frontpage',
            'GOOGLE_ANALYTICS_ACCOUNT': GOOGLE_ANALYTICS_ACCOUNT,
        }
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, args))

class EditFormHandler(webapp.RequestHandler):
    def get(self):
        key = self.request.path.split('/')[-2]
        context = db.get(key)

        if context.password != self.request.get('password'):
            self.error(403)
            return

        path = os.path.join(os.path.dirname(__file__), 'edit_ad_form.html')
        self.response.out.write(template.render(path, {
            'ad': context,
        }))

    def post(self):
        key = self.request.path.split('/')[-2]
        context = db.get(key)

        if context.password != self.request.get('password'):
            self.error(403)
            return

        context.title = self.request.get('title')
        context.blurb = self.request.get('blurb')
        context.phone = self.request.get('phone')
        context.email = self.request.get('email')
        context.price2 = int(self.request.get('price'))
        context.sold = 'sold' in self.request.arguments()
        context.put()

        self.redirect('/ads/' + key)

class SponsorsPage(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'sponsors.html')
        self.response.out.write(template.render(path, {
            'sponsors': Sponsor.all().order('-created').fetch(100),
            'body_id': 'sponsors_page',
            'GOOGLE_ANALYTICS_ACCOUNT': GOOGLE_ANALYTICS_ACCOUNT,
        }))

class BillboardsPage(webapp.RequestHandler):
    def get(self):
        args = {
            'ads': Ad.all().order('-created').fetch(100),
            'billboards': Billboard.all().order('-created').fetch(100),
            'body_id': 'billboards_page',
            'GOOGLE_ANALYTICS_ACCOUNT': GOOGLE_ANALYTICS_ACCOUNT,
        }
        path = os.path.join(os.path.dirname(__file__), 'billboards.html')
        self.response.out.write(template.render(path, args))

class AdViewHandler(webapp.RequestHandler):
    def get(self):
        key = self.request.path.split('/')[-1]
        ad = db.get(key)
        if ad:
            args = {
                'ad': ad,
                'billboards': db.get(ad.billboards),
                'qr': self.request.url,
                'body_id': 'ad_view',
                'GOOGLE_ANALYTICS_ACCOUNT': GOOGLE_ANALYTICS_ACCOUNT,
            }
            path = os.path.join(os.path.dirname(__file__), 'ad_view.html')
            self.response.out.write(template.render(path, args))
        else:
            self.error(404)

class AddFormHandler(webapp.RequestHandler):
    def get(self):
        args = {
            'billboards': Billboard.all(),
            'body_id': 'add_ad_form',
            'GOOGLE_ANALYTICS_ACCOUNT': GOOGLE_ANALYTICS_ACCOUNT,
        }
        path = os.path.join(os.path.dirname(__file__), 'add_ad_form.html')
        self.response.out.write(template.render(path, args))

    def post(self):
        title = self.request.get('title')
        blurb = self.request.get('blurb')
        phone = self.request.get('phone')
        image = self.request.get('image')
        email = self.request.get('email')
        price = self.request.get('price')

        image_thumb = images.resize(image, 100, 100)
        image_medium = images.resize(image, 480, 480)
        image_small = images.resize(image, 200, 200)
        billboards = self.request.get('selected_billboards')
        billboards = [db.Key(key) for key in billboards.split(' ')]

        ad = Ad(title=title)
        ad.ip = self.request.remote_addr
        ad.sold = False
        ad.blurb = blurb
        ad.image = db.Blob(image)
        ad.image_thumb = db.Blob(image_thumb)
        ad.image_medium = db.Blob(image_medium)
        ad.image_small = db.Blob(image_small)
        ad.phone = db.PhoneNumber(phone)
        ad.email = db.Email(email)
        ad.price2 = int(price)
        ad.billboards = billboards
        ad.put()

        ad.password = hashlib.md5(SALT + ad.ip + str(ad.key())).hexdigest()
        ad.save()

        for billboard in db.get(billboards):
            billboard.ads.append(ad.key())
            billboard.put()

        path = os.path.join(os.path.dirname(__file__), 'success.html')
        self.response.out.write(template.render(path, {
            'ad': ad,
            'secret_link': 'http://%s/ads/%s/edit?password=%s' % (self.request.host, ad.key(), ad.password)
        }))

class BillboardViewHandler(webapp.RequestHandler):
    def get(self):
        key = self.request.path.split('/')[-1]
        context = db.get(key)
        
        ads = db.get(context.ads)
        ads.reverse()
        ads = ads[:12]
        
        sponsors = db.get(context.sponsors)
        
        dummies = []
        for i in range(0, 6 - len(sponsors)):
            dummies.append('/static/sponsor.png')
        
        if context:
            args = {
                'context': context,
                'ads': ads,
                'sponsors': sponsors,
                'dummies': dummies,
                'body_id': 'billboard_view',
                'GOOGLE_ANALYTICS_ACCOUNT': GOOGLE_ANALYTICS_ACCOUNT,
            }
            if 'fullscreen' in self.request.arguments():
                template_file = 'fullscreen.html'
            else:
                template_file = 'billboard_view.html'
            path = os.path.join(os.path.dirname(__file__), template_file)
            self.response.out.write(template.render(path, args))
        else:
            self.error(404)

class AddBillboardFormHandler(webapp.RequestHandler):
    def get(self):
        args = {
            'body_id': 'add_billboard_form',
            'GOOGLE_ANALYTICS_ACCOUNT': GOOGLE_ANALYTICS_ACCOUNT,
        }
        path = os.path.join(os.path.dirname(__file__), 'add_billboard_form.html')
        self.response.out.write(template.render(path, args))

    @staticmethod
    def add(form):
        image_thumb = images.resize(form['image'], 100, 100)
        image_medium = images.resize(form['image'], 480, 480)
        image_small = images.resize(form['image'], 200, 200)
        billboard = Billboard(title=form['title'])
        billboard.phone = db.PhoneNumber(form['phone'])
        billboard.email = db.Email(form['email'])
        billboard.image = db.Blob(form.get('image'))
        billboard.image_thumb = db.Blob(image_thumb)
        billboard.image_medium = db.Blob(image_medium)
        billboard.image_small = db.Blob(image_small)
        billboard.put()

    def post(self):
        form = {
            'title': self.request.get('title'),
            'phone': self.request.get('phone'),
            'email': self.request.get('email'),
            'image': self.request.get('image'),
            'image_thumb': self.request.get('image'),
        }
        AddBillboardFormHandler.add(form)
        self.redirect('/billboards')

class AddSponsorForm(webapp.RequestHandler):
    def get(self):
        args = {
            'body_id': 'add_sponsor_form',
            'GOOGLE_ANALYTICS_ACCOUNT': GOOGLE_ANALYTICS_ACCOUNT,
        }
        path = os.path.join(os.path.dirname(__file__), 'add_sponsor_form.html')
        self.response.out.write(template.render(path, args))

    def post(self):
        title = self.request.get('title')
        image = db.Blob(self.request.get('image'))

        sponsor = Sponsor(title=title, image=image)
        sponsor.put()

        self.redirect('/sponsors')

class ImageHandler(webapp.RequestHandler):
    def get(self):
        key = self.request.path.split('/')[-2]
        context = db.get(key)
        if context.image:
            self.response.headers['Content-Type'] = "image/png"
            self.response.headers['Expires'] = "Thu, 15 Apr 2012 20:00:00 GMT"
            self.response.headers['Cache-control'] = "max-age=3600"
            size = self.request.get('size', 'normal')
            if size == 'normal':
                self.response.out.write(context.image)
            elif size == 'thumb':
                self.response.out.write(context.image_thumb)
            elif size == 'medium':
                self.response.out.write(context.image_medium)
            elif size == 'small':
                self.response.out.write(context.image_small)
        else:
            self.error(404)

class RescaleImages(webapp.RequestHandler):
    def get(self):
        json = []
        for m in Ad.all():
            if m.image:
                json.append({
                    'title': m.title,
                })
                image_thumb = images.resize(m.image, 100, 100);
                image_medium = images.resize(m.image, 480, 480);
                image_small = images.resize(m.image, 200, 200);
                m.image_thumb = db.Blob(image_thumb)
                m.image_small = db.Blob(image_small)
                m.put()
        for m in Billboard.all():
            if m.image:
                json.append({
                    'title': m.title,
                })
                image_thumb = images.resize(m.image, 100, 100);
                image_medium = images.resize(m.image, 480, 480);
                image_small = images.resize(m.image, 200, 200);
                m.image_thumb = db.Blob(image_thumb)
                m.image_small = db.Blob(image_small)
                m.put()
        json = simplejson.dumps(json)
        self.response.headers.add_header('Content-Type', 'application/json')
        self.response.out.write(json)

def main():
    urls = [
        ('/', MainHandler),
        ('/ads/.*/edit', EditFormHandler),
        ('/ads/.*/image', ImageHandler),
        ('/sponsors/.*/image', ImageHandler),
        ('/billboards/.*/image', ImageHandler),
        ('/ads/.*', AdViewHandler),
        ('/rescale', RescaleImages),
        ('/billboards', BillboardsPage),
        ('/sponsors', SponsorsPage),
        ('/billboards/.*', BillboardViewHandler),
        ('/add-billboard', AddBillboardFormHandler),
        ('/add-sponsor', AddSponsorForm),
        ('/add', AddFormHandler),
    ]
    application = webapp.WSGIApplication(urls, debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
