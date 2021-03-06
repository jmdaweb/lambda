#Addon for Lambda Math Editor
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.
#Copyright (C) 2016-2017 Alberto Zanella <lapostadialberto@gmail.com>

import config
import speech
import addonHandler
import appModuleHandler
import controlTypes
from . import lambdaProfileSetup
from lambdaEdit import LambdaDialogEdit,LambdaMainEditor
from NVDAObjects.window import DisplayModelEditableText

addonHandler.initTranslation()

class AppModule(appModuleHandler.AppModule):
# Dialogs which has edit fields like the main Lambda Editor
	_customDialogsNames = (
	"TStructureW", #Structure view Window
	"TFrm_Matrix", #Matrix Window
	"TFrm_Calculator_Simple", #Calculator 
	)
	
	def __init__(self, *args, **kwargs):
		super(AppModule, self).__init__(*args, **kwargs)
		if  (lambdaProfileSetup.profileExists()) :
			#We update the table abs path since the user should have a portable version and the path may be different.
			lambdaProfileSetup.updateTablePath()
		else: #If a lambda profile doesn't exists:
			lambdaProfileSetup.createLambdaProfile()
		lambdaProfileSetup.addBrailleTableToGUI()
	
	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if (obj.windowClassName == u'TJvEditor') : #Main editor windows
			clsList.insert(0, LambdaMainEditor)
		if  (obj.windowClassName == u'TEdit') and (obj.role == controlTypes.ROLE_EDITABLETEXT) :
			#Dialogs with enhanced spoken math text
			try :
				dialogW = obj.parent.parent
				if dialogW and dialogW.windowClassName in self._customDialogsNames :
					clsList.insert(0, LambdaDialogEdit)
					clsList.remove(DisplayModelEditableText)
			except : pass
		if obj.windowClassName == u'TLambdaEdit' :
		#Matrix dialog
			try :
				dialogW = obj.parent.parent
				if dialogW and dialogW.windowClassName in self._customDialogsNames :
					clsList.insert(0, LambdaMatrixEdit)
					clsList.remove(DisplayModelEditableText)
			except : pass
	
	#report input symbols general handler
	shouldValueChangeSpeak = False
	def reportLastInsertedText(self,obj,reason=None) :
		obj.detectPossibleSelectionChange()
		obj.invalidateCache()
		obj.redraw()
		s = obj.getLambdaObj().getlastinsertedel(obj.windowHandle, 1)
		if s == None or len(s) == 0 : return
		self.shouldValueChangeSpeak = False
		if config.conf['keyboard']['speakTypedCharacters']:
			speech.speakText(s)

	def force_symbol_speak(self) :
		self.shouldValueChangeSpeak = True
	
	def event_valueChange(self,obj,nh) :
		if isinstance(obj,LambdaMainEditor):
			if self.shouldValueChangeSpeak :
				self.reportLastInsertedText(obj,"value")
		return nh()
	
	def terminate(self) :
		super(AppModule, self).terminate()
		#Clean-up custom braille tables
		lambdaProfileSetup.removeBrailleTableToGUI()