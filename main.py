 #!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2, urllib, urllib2, webbrowser, json, requests, facebook, urllib3
import jinja2

import os
import logging

facebook_token = "EAAHrvXTrwm8BAGZAqzMetugocP36p4CM7tZCwiHUHMI2IE0V6DVOPze6mY4rNa01ZAz8dWbR1T4fKS6umP6kylJuHxG6mu9sLVbR2Uf6QZBT3QklUCfPt3rqeNbKkpjXe2yfcKs6aYdZB1QZAGJMuZCHuTfgZAd1pqJ8JgeJTA3EeAZDZD"

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        logging.info("In MainHandler")
             
        template_values={}
        template_values['page_title']="Friend to Lover"
        template = JINJA_ENVIRONMENT.get_template('greetform.html')
        self.response.write(template.render(template_values))
 
def safeGet(url):
    try:
        return urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        print 'The server couln\'t fulfill the request.'
        print 'Error code: ', e.code
    except urllib2.URLError, e:
        print 'We failed to reach a server'
        print 'Reason: ', e.reason
    return None

graph = facebook.GraphAPI(access_token=facebook_token)

def getName(id):
    host = "https://graph.facebook.com"
    path = "/" + id + "/friendlists"
    params = urllib.parse.urlencode({"access_token": token})

    url = "{host}{path}?{params}".format(host=host, path=path, params=params)
    return safeGet(url)

print(getFriend("745737652283210"))

class GreetResponseHandlr(webapp2.RequestHandler):
    def post(self):
        latlng = self.request.headers.get("X-AppEngine-CityLatLong",None)
        vals={}
        tag = self.request.get('tag')
        vals['page_title']="Flickr Tag Search Results: " + tag
                  
        if tag:
            tag = self.request.get('tag')
            vals['tag']=tag
            photos = [Photo(get_photo_info(photo_id)) for photo_id in get_photo_ids(tag,latlng)]
                    
            #Top Five Photos by Views
            topviews = sorted(photos, key=lambda x: x.num_views, reverse=True)
            topfiveviews = []
            for photo in topviews[:5]:
                topfiveviews.append(photo)
            vals['topfiveviews'] = topfiveviews
                    
            #The photo with the highest number of tags
            toptags = sorted(photos, key=lambda x: len(x.tags), reverse=True)
            toponetags = toptags[0]
            vals['toponetags'] = toponetags
                    
            #The photo with the highest number of comments
            topcomments = sorted(photos, key=lambda x: x.commentcount, reverse=True)
            toponecomments = topcomments[0]
            vals['toponecomments'] = toponecomments
                   
            template = JINJA_ENVIRONMENT.get_template('greetresponse.html')
            self.response.write(template.render(vals))                  
        else:
            template = JINJA_ENVIRONMENT.get_template('greetform.html')
            self.response.write(template.render(vals))
 
application = webapp2.WSGIApplication([ \
                                      ('/gresponse', GreetResponseHandlr),
                                      ('/.*', MainHandler)
                                      ], 
                                      debug=True)