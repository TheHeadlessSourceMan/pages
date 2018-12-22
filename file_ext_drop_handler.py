#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
A windows shell extension to implement a file icon drop handler
"""
import pythoncom
import win32con
from win32com.shell import shell,shellcon
import win32gui


class ShellExtension(object):
	"""
	A windows shell extension to implement a file icon drop handler
	"""
	_reg_progid_="Python.ShellExtension.DropHandler"
	_reg_desc_="Python Sample Shell Extension (drop handler)"
	_reg_clsid_="{CED0336C-C9EE-4a7f-8D7F-C660393C322F}"
	_reg_class_spec_="pages.file_ext_drop_handler.ShellExtension"
	_com_interfaces_=[shell.IID_IShellExtInit,pythoncom.IID_IDropTarget]
	_public_methods_=['DragEnter','DragOver','DragLeave','Drop'] + shellcon.IShellExtInit_Methods

	def __init__(self):
		self.dataobj=None

	def Initialize(self,folder,dataobj,hkey):
		"""
		Called when the class is initialized
		"""
		print "Init",folder,dataobj,hkey
		self.dataobj=dataobj

	def InvokeCommand(self,ci):
		"""
		Called when a command verb is invoked
		"""
		mask,hwnd,verb,params,directory,nShow,hotkey,hicon=ci
		win32gui.MessageBox(hwnd,"Hello","Wow",win32con.MB_OK)

	def GetCommandString(self,cmd,typ):
		"""
		Gets the command line passed in

		NOTE:
		If GetCommandString returns the same string for all items then
		the shell seems to ignore all but one.  This is even true in
		Win7 etc where there is no status bar (and hence this string seems
		ignored)
		"""
		return "Hello from Python (cmd=%d)!!" % (cmd,)

def DllRegisterServer():
	"""
	Register the service
	"""
	import _winreg
	key=_winreg.CreateKey(_winreg.HKEY_CLASSES_ROOT,".pages")
	subkey=_winreg.CreateKey(key,"ShellEx")
	subkey2=_winreg.CreateKey(subkey,"DropHandler")
	_winreg.SetValueEx(subkey2,None,0,_winreg.REG_SZ,ShellExtension._reg_clsid_)
	print ShellExtension._reg_desc_,"registration complete."

def DllUnregisterServer():
	"""
	Unregister the service
	"""
	import _winreg
	try:
		_winreg.DeleteKey(_winreg.HKEY_CLASSES_ROOT,".pages\\shellex\\DropHandler")
	except WindowsError,details:
		import errno
		if details.errno !=errno.ENOENT:
			raise details
	print ShellExtension._reg_desc_,"unregistration complete."


if __name__=='__main__':
	from win32com.server import register
	register.UseCommandLine(ShellExtension,
		finalize_register=DllRegisterServer,
		finalize_unregister=DllUnregisterServer)
