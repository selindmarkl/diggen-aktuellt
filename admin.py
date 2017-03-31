import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from model import Sponsor

class AdEditForm(webapp.RequestHandler):
    def get(self):
        key = self.request.path.split('/')[-2]
        path = os.path.join(os.path.dirname(__file__), 'admin_edit_ad_form.html')
        self.response.out.write(template.render(path, {
            'ad': db.get(key),
            'body_id': 'admin_view',
        }))

    def post(self):
        key = self.request.path.split('/')[-2]
        context = db.get(key)

        context.title = self.request.get('title')
        context.blurb = self.request.get('blurb')
        context.phone = self.request.get('phone')
        context.email = self.request.get('email')
        context.price2 = int(self.request.get('price'))
        context.sold = 'sold' in self.request.arguments()
        context.put()

        self.redirect('/ads/' + key)

    def delete(self):
        key = self.request.path.split('/')[-2]
        key = db.Key(key)
        context = db.get(key)

        title = context.title
        billboard_titles = []
        for billboard in db.get(context.billboards):
            billboard_titles.append(billboard.title)
            billboard.ads.remove(key)
            billboard.save()

        context.delete()

        self.response.headers['Content-Type'] = "text/plain"
        self.response.headers['Content-Length'] = "text/plain"
        self.response.out.write('Ad "%s" was deleted and removed from %s' % (title, ', '.join(billboard_titles)))

class BillboardEditForm(webapp.RequestHandler):
    def get(self):
        key = self.request.path.split('/')[-2]
        context = db.get(key)
        args = {
            'context': context,
            'sponsors': Sponsor.all().fetch(100),
            'selected_sponsors': ' '.join([str(i) for i in context.sponsors]),
        }
        path = os.path.join(os.path.dirname(__file__), 'admin_edit_billboard_form.html')
        self.response.out.write(template.render(path, args))

    def post(self):
        key = self.request.path.split('/')[-2]
        context = db.get(key)
        
        context.title = self.request.get('title')
        context.phone = self.request.get('phone')
        context.email = self.request.get('email')
        
        sponsors = self.request.get('selected_sponsors')
        sponsors = [db.Key(i) for i in sponsors.split(' ')]
        context.sponsors = sponsors
        
        context.put()
        self.redirect('/billboards/' + key)

def main():
    urls = [
        ('/ads/.*/admin', AdEditForm),
        ('/billboards/.*/admin', BillboardEditForm),
    ]
    application = webapp.WSGIApplication(urls, debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
