import os,glob

# ========= format info for pyformatgenie =========
try:
	import pyformatgenie
	guid='{27e64577-726f-4488-9aa9-aaa5960d0092}'
	pfg=pyformatgenie.PyFormatGenie()
	if pfg.format(guid)==None: # is the guid already registered?
		# did not have the format registered, so do so now
		format=pfg.addFormat(
			guid, # registering the same id
			filetypeImport='pages', # the name of this module
			filetypeClass='Pages', # the name of the class that represents an open file
			name='pagesFile',
			description='a list of webpages to be opened simultaneously',
			dataFamilies=[],
			iconLocation=os.path.abspath(__file__).rsplit(os.sep,1)[0]+os.sep+'pages.ico', # the icon is relative to this location
			filenamePatterns=['*.pages','*.urls','*.links','*.url'],
			mimeTypes=['wwwserver/redirection','application/internet-shortcut','application/x-url','message/external-body','text/url','text/x-url'],
			magicNumber=None) # the magic number would be the same as a zip file, and therefore, not deterministic
		# --- actions ---
		format.addAction('browse',objName='browseAll')
		# and the most important part...
		pfg.save()
except ImportError,e:
	# pyformatgenie is not installed (yet?). Continue with whatever you came here for.
	pass

	
class Visited:
	"""
	Wrap an array in an object to make it globally mutable
	"""
	def __init__(self):
		self.visited=[]

		
def fileUrlToPath(filename):
	"""
	convert any filename (including those that start with file://)
	to an absolute system path
	"""
	if filename.startswith('file://'):
		filename=filename.split('://',1)[-1]
		if os.sep!='/':
			if len(filename)>1:
				if filename[1]=='|':
					filename[1]=':'
				filename=filename.replace('/',os.sep)
	return os.path.abspath(filename)
		
		
def pages(filename,allowGlob=True,visitedPages=None):
	"""
	filename can be:
		.pages, .urls, .links file
		.url file
		any browseable file
		any browseable url
		a filename including glob wildcards (eg *.url)
		an array of any of that stuff
		
	allowGlob - enable/disable glob wildcards
		
	visitedPages - no need to set this.  It is only used to make sure
		we don't get in an infinite loop or bring up a bunch of the same page.
	"""
	ret=[]
	if visitedPages==None:
		visitedPages=Visited()
	if type(filename)==list: # open each element in a list
		for p in filename:
			ret.extend(pages(p,allowGlob=allowGlob,visitedPages=visitedPages))
		return ret
	filename=fileUrlToPath(filename)
	if allowGlob: # split out glob expressions
		for name in glob.glob(unicode(filename)): # (casting to unicode allows glob to return unicode filenames)
			ret.extend(pages(name,allowGlob=False,visitedPages=visitedPages))
	else: # read an individual file
		filename=os.path.abspath(filename)
		if filename in visitedPages.visited:
			return ret
		visitedPages.visited.append(filename)
		ext=filename.rsplit('.',1)[-1].lower()
		if ext in ['pages','urls','links']: # read a pages file
			pgs=Pages(filename)
			ret.extend(pgs.pages(visitedPages=visitedPages))
		elif ext=='url': # read a url file
			f=open(filename,'r')
			for line in f:
				line=line.strip()
				if line.startswith('URL='):
					line=line.split('=',1)[-1].strip()
					if line not in visitedPages.visited:
						ret.append(line)
						visitedPages.visited.append(line)
					break
			f.close()
		else: # any other type of file, open in browser
			ret.append(filename)
	return ret

def isBrowserRunning(browser='firefox'):
	"""
	check to see if the browser is running
	"""
	import subprocess
	ps='powershell '
	psCMD='get-process "'+browser+'"'
	cmd=ps+psCMD
	p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	out,err=p.communicate()
	out=out.strip()
	err=err.strip()
	#print 'OUT'
	#print out
	#print 'ERR'
	#print err
	return out.startswith('Handles')
	
def browseAll(pages,browser='"c:\\Program Files\\Mozilla Firefox\\firefox.exe"',newWindow=True):
	"""
	browse one or more pages
	"""
	import subprocess
	if type(pages)!=list:
		pages=[pages]
	if len(pages)<1:
		return
	if newWindow or not isBrowserRunning(): # if there is no window we need to create one
		if len(pages)<2: # if there is only one url, need to specify new window
			cmd=browser+' -new-window "'+pages[0]+'"'
		else: # if there are multiple urls, ff will open them all in a new window
			cmd=browser+' '+(' '.join(['"'+url+'"' for url in pages]))
		p=subprocess.Popen(cmd)
	else:
		# need to run each as individual command
		for url in pages:
			cmd=browser+' "'+url+'"'
			p=subprocess.Popen(cmd)
	
class Pages:
	"""
	a .pages, .urls, .links file is simply a list of urls
	(lines beginning with # are comments)
	
	The power of this is that you can open a browser with
	several related pages all at once!
	
	Some sample urls that work:
		https://www.google.com
		file:///home/~zabrowski/www/page.html
		page.html
		other_pages.pages
		link.url
		*.url
	"""
	def __init__(self,filename=None):
		self.filename=None
		self.allLines=[]
		if filename!=None:
			self.load(filename)
			
	def load(self,filename,append=False):
		"""
		load a .pages, .urls, .links file
		
		you can choose to append or overwrite exsiting urls
		"""
		self.filename=fileUrlToPath(filename)
		if append==False:
			self.allLines=[]
		f=open(filename,'rb')
		for line in f:
			line=line.strip()
			self.allLines.append(line)
				
	def save(self,filename):
		"""
		save this as a .pages file
		"""
		f=open(filename,'wb')
		for p in self.allLines:
			f.write(p)
			f.write('\n')
		f.close()
		
	def pages(self,visitedPages=None):
		"""
		gets a list of all pages that will be visited by this file
		
		visitedPages - no need to set this.  It is only used to make sure
			we don't get in an infinite loop or bring up a bunch of the same page.
		"""
		if visitedPages==None:
			visitedPages=Visited()
		#if self.filename!=None:
		#	if self.filename in visitedPages:
		#		return []
		#	visitedPages.append(self)
		ret=[]
		for p in self.allLines:
			if len(p)==0 or p[1]=='#':
				continue
			protoidx=p.find('://')
			if protoidx<3 or protoidx>9:
				if not os.path.isabs(p):
					p=self.filename.rsplit(os.sep,1)[0]+os.sep+p
				ret.extend(pages(p,allowGlob=True,visitedPages=visitedPages))
			elif p.startswith('file://'):
				ret.extend(pages(p,allowGlob=True,visitedPages=visitedPages))
			elif p not in visitedPages.visited:
				ret.append(p)
				visitedPages.visited.append(p)
		return ret
		
	def add(self,url):
		"""
		add a new url to the pages
		
		NOTE: This can be:
			a proper url
			a local file
			another .pages, .urls, .links file
			a .url file (windows internet shortcut)
		"""
		self.allLines.append(url)
		
	def browseAll(self,browser='"c:\\Program Files\\Mozilla Firefox\\firefox.exe"',newWindow=True):
		"""
		open all urls in a browser
		"""
		browseAll(self.pages(),browser,newWindow)
		
			
if __name__ == '__main__':
	import sys
	# Use the Psyco python accelerator if available
	# See:
	# 	http://psyco.sourceforge.net
	try:
		import psyco
		psyco.full() # accelerate this program
	except ImportError:
		pass
	if len(sys.argv)<2:
		print 'Opens all pages in a .pages, .urls, .links page list file in a browser'
		print 'USEAGE:'
		print '   pages.py whatever.pages [also.pages ...]'
	else:
		pgs=pages(sys.argv[1:])
		browseAll(pgs)