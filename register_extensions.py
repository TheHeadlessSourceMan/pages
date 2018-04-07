try:
	import _winreg as winreg
except:
	import winreg
	
def _register(extension,icon=None,verbs={},description=None,shortcutOverlay=False,shellExtensions={}):
	"""
	extension - file extension to register (starting with ".")
	icon - path to the icon for this extension
	verbs - a dict of {name:commandline} for example {'open':'notepad.exe "%1"'}
	description - a longer text description
	shortcutOverlay - tell the shell to draw the "shortcut" arrow over the icon
	shellExtensions - {type:classid} register code to handle things like thumbnails, dragdrop, etc
		see: https://msdn.microsoft.com/en-us/library/windows/desktop/cc144067(v=vs.85).aspx
	"""
	key=winreg.CreateKeyEx(winreg.HKEY_CLASSES_ROOT,extension)
	if description:
		winreg.SetValue(winreg.HKEY_CLASSES_ROOT,extension,winreg.REG_SZ,description)
	if icon:
		winreg.SetValue(key,'DefaultIcon',winreg.REG_SZ,icon)
	if shortcutOverlay:
		winreg.SetValueEx(key,'IsShortcut',0,winreg.REG_SZ,'')
	else:
		try:
			winreg.DeleteKey(key,'IsShortcut')
		except Exception:
			pass
	if len(verbs)>0:
		subkey=winreg.CreateKeyEx(key,'Shell')
		for name,commandline in verbs.items():
			shortname=name.replace(' ','')
			verbKey=winreg.CreateKeyEx(subkey,shortname)
			if shortname!=name:
				winreg.SetValue(verbKey,shortname,winreg.REG_SZ,name)
			winreg.CreateKeyEx(verbKey,'command')
			winreg.SetValue(verbKey,'command',winreg.REG_SZ,commandline)
	if len(shellExtensions)>0:
		subkey=winreg.CreateKeyEx(key,'ShellEx')
		for typename,clsid in shellExtensions.items():
			winreg.CreateKeyEx(subkey,typename)
			winreg.SetValue(subkey,typename,winreg.REG_SZ,clsid)
			
if __name__ == '__main__':
	import os
	import sys
	import win32com.shell.shell as shell
	import file_ext_drop_handler
	ASADMIN = 'asadmin'
	# run this elevated
	if sys.argv[-1] != ASADMIN:
		script = os.path.abspath(sys.argv[0])
		params = ' '.join([script] + sys.argv[1:] + [ASADMIN])
		shell.ShellExecuteEx(lpVerb='runas', lpFile=sys.executable, lpParameters=params)
		sys.exit(0)
	dropHandlerClsid=file_ext_drop_handler.ShellExtension._reg_clsid_
	here=os.path.abspath(__file__).rsplit(os.sep,1)[0]+os.sep
	_register('.pages',
		icon=here+'pages.ico',
		verbs={'open':'python "'+here+'pages.py" "%1"','notepad':'notepad "%1"'},
		shortcutOverlay=True, # since this is equivilent to an "internet shortcut"
		shellExtensions={'DropHandler':dropHandlerClsid}
		)
	_register('.urls',
		icon=here+'pages.ico',
		verbs={'open':'python "'+here+'pages.py" "%1"','notepad':'notepad "%1"'},
		shortcutOverlay=True, # since this is equivilent to an "internet shortcut"
		shellExtensions={'DropHandler':dropHandlerClsid}
		)
	_register('.links',
		icon=here+'pages.ico',
		verbs={'open':'python "'+here+'pages.py" "%1"','notepad':'notepad "%1"'},
		shortcutOverlay=True, # since this is equivilent to an "internet shortcut"
		shellExtensions={'DropHandler':dropHandlerClsid}
		)
