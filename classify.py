import os
import cgi
import re
import simplejson
import urllib2

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch


class MainPage(webapp.RequestHandler):
	def get(self):
		
		title = 'Fusion Tables Data Classify Wizard'
		page_values = {
						'title': title
						
						}
		
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, page_values))
		
class GetColumns(webapp.RequestHandler):
	def post(self):
		columnList = []
		
		tableid = cgi.escape(self.request.get('tid'))
		
		# retrieve columns from fusion table as json
		url = 'http://www.google.com/fusiontables/api/'
		query = 'query?sql=DESCRIBE ' + tableid + '&jsonCallback=foo'
		query = query.replace(' ','%20')
		# query = unicode(query, "utf-8")
		jsonpdata = urlfetch.fetch(url+query).content
		jsondata = re.sub(r'^[^{]*|\)$', '', jsonpdata) 
		data = simplejson.loads(jsondata)
		columns = data['table']['rows'] 
		
		for item in columns:
			colName = item[1]
			colType = item[2]
			
			if colType == 'number':
				columnList.append(colName)
		
		columnList2 = simplejson.dumps(columnList)
		
		title = 'Fusion Tables Data Classify Wizard'
		
		page_values = {
					'title': title,
					'tableid': tableid,
					'columns': columnList2
					}
		
		path = os.path.join(os.path.dirname(__file__), 'home.html')
		self.response.out.write(template.render(path, page_values))
		
class Classify(webapp.RequestHandler):
	def post(self):
		tableid = cgi.escape(self.request.get('tid'))
		column = cgi.escape(self.request.get('column'))
		classno = cgi.escape(self.request.get('classno'))
		classmethod = cgi.escape(self.request.get('classmethod'))
		
		
		
		
		

application = webapp.WSGIApplication(
									[('/', MainPage),
									('/getcolumns', GetColumns),
									('/classify', Classify)
									],
									debug=True)

def main():
	run_wsgi_app(application)
	
if __name__ == "__main__":
	main()
				  
