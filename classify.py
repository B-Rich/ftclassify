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
		classno_ = int(classno)
		classmethod = cgi.escape(self.request.get('classmethod'))
		classmethod_ = int(classmethod)
		
		dList = []
				
		# retrieve row data from fusion table as json
		url = 'http://www.google.com/fusiontables/api/'
		query = 'query?sql=SELECT ' + column + ' FROM ' + tableid + '&jsonCallback=foo'
		query = query.replace(' ','%20')
		#query = unicode(query, "utf-8")
		jsonpdata = urlfetch.fetch(url+query).content
		jsondata = re.sub(r'^[^{]*|\)$', '', jsonpdata) 
		data = simplejson.loads(jsondata)
		data2 = data['table']['rows'] 
	
		for item in data2:
			dList.append(item[0])
				
		
		def getEqualInterval(dList, classno):
			minValue = min(dList)
			maxValue = max(dList)
			
			interval = (maxValue - minValue)/classno
			lower = minValue
			
			classes = [lower]
		
			for i in range(classno):
				upper = lower + interval
				classes.append(upper)
				lower = upper
				
				
			return classes
		
		def getQuantiles(dList, classno):
			dList.sort()
			
			# class breaks
			breaks = len(dList) / classno
			interval = breaks
			
			# breaks List
			classes = [dList[0]]
			if len(dList) % classno == 0:
				while breaks < len(dList):
					classes.append(dList[breaks - 1])
					breaks += interval
			
			else: 
				while breaks < len(dList):
					classes.append(dList[breaks - 1])
					breaks += interval
				classes.pop()
				classes.append(dList[len(dList) - 1])
			
			
			return classes

		
		
		def getJenksBreaks(dataList, numClass):
			dataList.sort()
			mat1 = []
			for i in range(0,len(dataList)+1):
				temp = []
				for j in range(0,numClass+1):
					temp.append(0)
				mat1.append(temp)
			mat2 = []
			for i in range(0, len(dataList)+1):
				temp = []
				for j in range(0,len(dataList)+1):
					temp.append(0)
				mat2.append(temp)
			for i in range(1, numClass+1):
				mat1[1][i] = 1
				mat2[1][i] = 0
				for j in range(2,len(dataList)+1):
					mat2[j][i] = float('inf')
			v = 0.0
			for l in range(2,len(dataList)+1):
				s1 = 0.0
				s2 = 0.0
				w = 0.0
				for m in range(1, l+1):
					i3 = l - m + 1
					val = float(dataList[i3-1])
					s2 += val * val
					s1 += val
					w += 1
					v = s2 - (s1 * s1) / w
					i4 = i3 - 1
					if i4 != 0:
						for j in range(2,numClass+1):
							if mat2[l][j] >= (v + mat2[i4][j - 1]):
								mat1[l][j] = i3
								mat2[l][j] = v + mat2[i4][j - 1]
				mat1[l][1] = 1
				mat2[l][1] = v
			k = len(dataList)
			kclass = []
			for i in range(0,numClass+1):
				kclass.append(0)
			kclass[numClass] = float(dataList[len(dataList) - 1])
			countNum = numClass
			while countNum >= 2:#print "rank = " str(mat1[k][countNum])
				id = int((mat1[k][countNum]) - 2)
				
				kclass[countNum - 1] = dataList[id]
				k = int((mat1[k][countNum] - 1))
				countNum -= 1
			return kclass
				
					
		if classmethod_ == 1:
			cList = getEqualInterval(dList, classno_)
		elif classmethod_ == 2:
			cList = getJenksBreaks(dList, classno_)
		elif classmethod_ == 3:
			cList = getQuantiles(dList, classno_)
		else:
			cList = getEqualInterval(dList, classno_)
			
		
		
		title = 'Fusion Tables Data Classify Wizard'

		page_values = {
					'title': title,
					'classes': cList
					}
		
		path = os.path.join(os.path.dirname(__file__), 'results.html')
		self.response.out.write(template.render(path, page_values))
	
		

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
				  
