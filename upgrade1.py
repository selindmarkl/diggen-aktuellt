import hashlib
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from main import Ad
from main import SALT

class UpgradeHandler(webapp.RequestHandler):

    def get(self):
        lines = []

        for ad in Ad.all():
            ad.sold = False
            ad.ip = ad.ip or self.request.remote_addr
            ad.password = hashlib.md5(SALT + ad.ip + str(ad.key())).hexdigest()
            ad.save()
            lines.append(ad.title + ' ' + ad.password)

        self.response.headers.add_header('Content-Type', 'text/plain')
        self.response.out.write('\n'.join(lines))

def main():
    urls = [
        ('/upgrade', UpgradeHandler),
    ]
    application = webapp.WSGIApplication(urls, debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
