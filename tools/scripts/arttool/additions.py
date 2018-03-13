# ==============================================================================
# Copyright (C) 2017 General Workings Inc
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
# ==============================================================================


# ==============================================================================
# IMPORTS
# ==============================================================================
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QListWidget, QVBoxLayout, QTabWidget
from PyQt5.QtWidgets import QPushButton, QComboBox, QDateTimeEdit, QDialogButtonBox, QMessageBox
from PyQt5.QtWidgets import QScrollArea, QMainWindow, QCheckBox, QHBoxLayout, QTextEdit
from PyQt5.QtWidgets import QLineEdit, QFrame, QDialog, QFrame, QSplitter
from PyQt5.QtGui import QIcon, QBrush, QColor, QFont, QPixmap, QMovie
from PyQt5.QtCore import QDateTime, Qt


ADDITION_TYPES = ["Image","Sequence","Material","Model","Emitter","Tweak"]

ADDITION_IMAGE = { "type" : "image", 
				   "name" : "",
				   "file" : "" }

ADDITION_SEQUENCE = { "type" : "image", 
					  "name" : "",
					  "image" : "",
					  "rows" : 1,
					  "cols" : 1,
					  "first" : 0,
					  "last" : 0,
					  "rate" : 1.0,
					  "mode" : "repeat" }
					  
ADDITION_MATERIAL = {"type" : "material",
 					 "name" : "",
					 "image" : "texture,diffuse-0",
					 "culling" : "back",
					 "depth-test" : "less",
					 "depth-only" : False,
					 "opaque" : True}
			
ADDITION_MODEL = { "type" : "model",
				   "mesh" : "",
				   "material" : "" }
					  
ADDITION_EMITTER = { "type" : "emitter",
					 "model" : "",
					 "lifetime" : 1.0,
					 "scale-start" : 1.0,
					 "scale-end" : 2.0,
					 "alpha-start" : 1.0,
					 "alpha-end" : 0.0,
					 "num-particles" : 100,
					 "world-space" : True,
					 "inverse-rate" : False,
					 "z-sort-offset" : 0.0,
					 "rate-min" : 1.0,
					 "rate-max" : 1.0,
					 "friction-min" : 1.0,
					 "friction-max" : 1.0,
					 "force-min" : [0.0, 10.0, 0.0],
					 "force-max" : [0.0, 10.0, 0.0],
					 "initial-velocity-min" : [0.0, -40.0, 0.0],
					 "initial-velocity-max" : [0.0, -40.0, 0.0] }
					  
ADDITIONS = { "image" : ADDITION_IMAGE, 
			  "sequence" : ADDITION_SEQUENCE,
			  "material" : ADDITION_MATERIAL,
			  "model" : ADDITION_MODEL,
			  "emitter" : ADDITION_EMITTER }

# ==============================================================================
# NEW ADDITION DIALOG
# ==============================================================================

class NewAdditionDialog(QDialog):

	def __init__(self, parent):
		super(NewAdditionDialog, self).__init__(parent)

		self.combo = QComboBox(self)
		for s in ADDITION_TYPES:
			self.combo.addItem(s)
		self.combo.setCurrentIndex(0)
		self.combo.setGeometry(10, 10, 200, 30)
		
		# OK and Cancel buttons
		buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
		buttons.accepted.connect(self.accept)
		buttons.rejected.connect(self.reject)
		buttons.setParent(self)
		buttons.setGeometry(10, 40, 200, 30)
		
	@staticmethod
	def go_modal(parent = None):
		dialog = NewAdditionDialog(parent)
		result = dialog.exec_()
		if result == QDialog.Accepted:
			sel = ADDITION_TYPES[dialog.combo.currentIndex()]
			addn = ADDITIONS[sel.lower()]
			return AdditionDialog.go_modal(parent, addn)
		return None


# ==============================================================================
# ADDITION DIALOG
# ==============================================================================

FW = 180
PW = 400
	
class AdditionDialog(QDialog):

	def __init__(self, parent, addition):
		super(AdditionDialog, self).__init__(parent)

		self.addition = addition

		numitems = len(self.addition)
		
		x = 10
		y = 10
		dy = 40
		count = 0
		for field in self.addition:
			self.createLabelWidget(self, field, x, y, field in ["type"])
			y += dy
			count += 1
			if numitems > 10 and count >= (numitems / 2):
				y = 10
				x += PW + 10
				numitems = 0
				
		y += dy
		
		# OK and Cancel buttons
		buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
		buttons.accepted.connect(self.accept)
		buttons.rejected.connect(self.reject)
		buttons.setParent(self)
		buttons.setGeometry(10, y, 500, 30)
		
	# --------------------------------------------------
	# Create generic widget
	# --------------------------------------------------
	def createLabelWidget(self, parent, field, x, y, noedit=False):
	
		q = QLabel(field)
		q.setParent(parent)
		q.setGeometry(x, y, FW - 10, 36)
		q.setFont(QFont( "Arial", 12, QFont.Bold ))
		q.show()

		value = self.addition[field]
		
		if type(value) is str or type(value) is int or type(value) is float:
			if noedit:
				q = QLabel(str(value))
			else:
				q = QLineEdit(str(value))
				q.textChanged.connect(lambda text: self.onTextFieldChanged(text, field))			
		elif type(value) is bool:
			q = QCheckBox()
			q.setChecked(value)
			q.stateChanged.connect(lambda state: self.onCheckboxChanged(state, field))
		elif type(value) is list:
			xx = x + FW
			idx = 0
			for val in value:
				q = QLineEdit(str(val))
				q.setParent(parent)
				q.setGeometry(xx, y, 75, 30)
				q.setFont(QFont( "Arial", 12, QFont.Bold ))
				q.show()
				xx += 80
				q.textChanged.connect(lambda text, idx=idx: self.onTextFieldChanged(text, field, idx))
				idx += 1
						
		if type(value) is not list:
			q.setParent(parent)
			q.setGeometry(x + FW, y, PW - FW - 10, 30)
			q.show()
			q.setFont(QFont( "Arial", 12, QFont.Bold ))

			
	# text field changed
	def onTextFieldChanged(self, text, field, index=0):
		v = self.addition[field]
		
		if type(v) is str:
			self.addition[field] = text
		elif type(v) is int:
			self.addition[field] = int(text)
		elif type(v) is float:
			self.addition[field] = float(text)
		elif type(v) is list:
			print(v)
			print(text)
			print(field)
			print(index)
			# all vectors are floats
			self.addition[field][index] = float(text)
			
	# checkbox changed
	def onCheckboxChanged(self, state, field):
		if state == 0:
			self.addition[field] = False
		else:
			self.addition[field] = True

			
	@staticmethod
	def go_modal(parent, addition):
		dialog = AdditionDialog(parent, addition)
		result = dialog.exec_()
		if result == QDialog.Accepted:
			return dialog.addition
		return None
		
		