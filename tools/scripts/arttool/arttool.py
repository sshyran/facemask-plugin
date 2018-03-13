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
import sys, subprocess, os, json, uuid
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QListWidget, QVBoxLayout, QTabWidget
from PyQt5.QtWidgets import QPushButton, QComboBox, QDateTimeEdit, QDialogButtonBox, QMessageBox
from PyQt5.QtWidgets import QScrollArea, QMainWindow, QCheckBox, QHBoxLayout, QTextEdit
from PyQt5.QtWidgets import QLineEdit, QFrame, QDialog, QFrame, QSplitter
from PyQt5.QtGui import QIcon, QBrush, QColor, QFont, QPixmap, QMovie
from PyQt5.QtCore import QDateTime, Qt
from arttool.utils import *
from arttool.additions import *
	
	

# ==============================================================================
# MAIN WINDOW : ArtToolWindow class
# ==============================================================================
	
FIELD_WIDTH = 180
PANE_WIDTH = 690
TEXTURE_SIZES = ["32","64","128","256","512","1024","2048"]
MASK_UI_FIELDS = { "name" : "Pretty Name",
				   "description" : "Description",
				   "author" : "Author",
				   "tags" : "Tags",
				   "category" : "Category",
				   "uuid" : "UUID",
				   "depth_head" : "Depth Head",
				   "is_morph" : "Morph Mask",
				   "is_vip" : "V.I.P. Mask",
				   "do_not_release" : "DO NOT RELEASE",
				   "texture_max" : "Max Texture Size",
				   "license" : "License",
				   "website" : "Website" }

	
class ArtToolWindow(QMainWindow): 

	# --------------------------------------------------
	# CONSTRUCTOR
	# --------------------------------------------------
	def __init__(self, *args): 
		super(ArtToolWindow, self).__init__(*args) 
 
		# Load our config
		self.config = createGetConfig()
 
		# Get list of fbx files
		self.fbxfiles = getFileList(".")
		
		# Left Pane
		leftPane = QWidget()
		leftLayout = QVBoxLayout(leftPane)

		# Streamlabs logo
		slabslogo = QLabel()
		slabslogo.setPixmap(QPixmap("arttool/streamlabs.png"))
		slabslogo.setScaledContents(True)
		slabslogo.show()
		leftLayout.addWidget(slabslogo)
		slabslogo.setMaximumWidth(300)
		slabslogo.setMaximumHeight(53)
		
		# Filter box
		self.fbxfilter = QLineEdit()
		leftLayout.addWidget(self.fbxfilter)
		
		# make a list widget
		self.fbxlist = QListWidget()
		for fbx in self.fbxfiles:
			self.fbxlist.addItem(fbx[2:])
		self.fbxlist.itemClicked.connect(lambda: self.onFbxClicked())
		self.fbxlist.setParent(leftPane)
		self.fbxlist.setMinimumHeight(560)
		leftLayout.addWidget(self.fbxlist)

		# top splitter
		topSplitter = QSplitter(Qt.Horizontal)
		topSplitter.addWidget(leftPane)

		# Layout for edit pane
		rightPane = QWidget()
		self.mainLayout = QHBoxLayout(rightPane)
		topSplitter.addWidget(rightPane)
		
		# Edit pane 
		self.editPane = None
		self.createMaskEditPane(None)
		
		# color fbxlist items
		for idx in range(0, len(self.fbxfiles)):
			self.setFbxColorIcon(idx)
			self.fbxlist.item(idx).setFont(QFont( "Arial", 12, QFont.Bold ))
			
		# crate main splitter
		mainSplitter = QSplitter(Qt.Vertical)
		mainSplitter.addWidget(topSplitter)
		
		# bottom pane
		bottomPane = QWidget()
		bottomArea = QHBoxLayout(bottomPane)
		
		# output window
		self.outputWindow = QTextEdit()
		self.outputWindow.setMinimumHeight(90)
		bottomArea.addWidget(self.outputWindow)

		# buttons area
		buttonArea = QWidget()
		buttonArea.setMinimumWidth(150)
		buttonArea.setMinimumHeight(60)
		locs = [(0,0),(0,30),(0,60),(75,0),(75,30),(75,60)]
		c = 0
		for nn in ["Refresh", "Autobuild", "Rebuild All", "Make Release", "SVN Update", "SVN Commit"]:
			b = QPushButton(nn)
			b.setParent(buttonArea)
			(x,y) = locs[c]
			c += 1
			b.setGeometry(x,y,75,30)
		bottomArea.addWidget(buttonArea)
		
		mainSplitter.addWidget(bottomPane)
			
		# Show the window
		self.setCentralWidget(mainSplitter)
		self.setGeometry(self.config["x"], self.config["y"], 1024, 768)
		self.setWindowTitle('Streamlabs Art Tool')
		self.setWindowIcon(QIcon('arttool/arttoolicon.png'))
		
		# State
		self.metadata = None 
		self.currentFbx = -1
		
		# Check our binaries
		self.checkBinaries()

	def checkBinaries(self):
		gotSVN = os.path.exists(SVNBIN.replace('"',''))
		gotMM = os.path.exists(MASKMAKERBIN)
		gotRP = os.path.exists(MORPHRESTFILE)
		
		if not gotSVN:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Information)
			msg.setText("You seem to be missing " + os.path.basename(SVNBIN))
			msg.setInformativeText("You should (re)install tortoiseSVN, and be sure to install the command line tools.")
			msg.setWindowTitle("Missing Binary File")
			msg.setStandardButtons(QMessageBox.Ok)
			msg.exec_()
		if not gotMM:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Information)
			msg.setText("You seem to be missing " + os.path.basename(MASKMAKERBIN))
			msg.setWindowTitle("Missing Binary File")
			msg.setStandardButtons(QMessageBox.Ok)
			msg.exec_()
		if not gotRP:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Information)
			msg.setText("You seem to be missing " + os.path.basename(MORPHRESTFILE))
			msg.setWindowTitle("Missing Binary File")
			msg.setStandardButtons(QMessageBox.Ok)
			msg.exec_()
			
	# --------------------------------------------------
	# Create generic widget
	# --------------------------------------------------
	def createLabelWidget(self, parent, name, field, y, noedit=False):
		q = QLabel(name)
		q.setParent(parent)
		q.setGeometry(10, y, FIELD_WIDTH-10, 36)
		q.setFont(QFont( "Arial", 12, QFont.Bold ))
		q.show()

		if field == None:
			return q
		
		value = self.metadata[field]
		
		if type(value) is str:
			if noedit:
				q = QLabel(value)
			else:
				q = QLineEdit(value)
				q.textChanged.connect(lambda text: self.onTextFieldChanged(text, field))
			if critical(field) and len(value) == 0:
				q.setStyleSheet("border: 1px solid #FF0000;")
			elif desired(field) and len(value) == 0:
				q.setStyleSheet("border: 1px solid #FF7F50;")
			else:
				q.setStyleSheet("border: 0px;")
		elif type(value) is bool:
			q = QCheckBox()
			q.setChecked(value)
			q.stateChanged.connect(lambda state: self.onCheckboxChanged(state, field))
		elif type(value) is int:
			q = QComboBox()
			idx = 0
			selidx = 0
			for s in TEXTURE_SIZES:
				if int(s) == value:
					selidx = idx
				q.addItem(s)
				idx += 1
			q.setCurrentIndex(selidx)
			q.currentIndexChanged.connect(lambda state: self.onTextureSizeChanged(state, field))
			
		q.setParent(parent)
		if type(value) is int:
			q.setGeometry(FIELD_WIDTH, y, FIELD_WIDTH, 30)
		else:
			q.setGeometry(FIELD_WIDTH, y, PANE_WIDTH - FIELD_WIDTH - 10, 30)
		q.setFont(QFont( "Arial", 12, QFont.Bold ))
		q.show()
		return q
	
	# --------------------------------------------------
	# Colors and Icons for main FBX list
	# --------------------------------------------------
	def setFbxColorIconInternal(self, mdc, mt, idx):
		if mdc == CHECKMETA_GOOD:
			self.fbxlist.item(idx).setForeground(QBrush(QColor("#32CD32")))
		elif mdc == CHECKMETA_ERROR:
			self.fbxlist.item(idx).setForeground(QBrush(QColor("#FF0000")))
		elif mdc == CHECKMETA_WARNING:
			self.fbxlist.item(idx).setForeground(QBrush(QColor("#FF7F50")))
		elif mdc == CHECKMETA_NORELEASE:
			self.fbxlist.item(idx).setForeground(QBrush(QColor("#000000")))
			
		if mt == MASK_UNKNOWN:
			self.fbxlist.item(idx).setIcon(QIcon("arttool/unknownicon.png"))
		elif mt == MASK_NORMAL:
			self.fbxlist.item(idx).setIcon(QIcon("arttool/maskicon.png"))
		elif mt == MASK_MORPH:
			self.fbxlist.item(idx).setIcon(QIcon("arttool/morphicon.png"))

	def setFbxColorIcon(self, idx):
		mdc,mt = checkMetaDataFile(self.fbxfiles[idx])
		self.setFbxColorIconInternal(mdc, mt, idx)

	def updateFbxColorIcon(self):
		mdc,mt = checkMetaData(self.metadata)
		self.setFbxColorIconInternal(mdc, mt, self.currentFbx)
			
			
	# --------------------------------------------------
	# createMaskEditPane
	# --------------------------------------------------
	def createMaskEditPane(self, fbxfile):
		if self.editPane:
			self.mainLayout.removeWidget(self.editPane)
			self.editPane.deleteLater()
	
		self.editPane = QWidget()
		self.mainLayout.addWidget(self.editPane)
		self.editPane.setMinimumWidth(PANE_WIDTH)
		self.editPane.show()

		# empty pane
		if fbxfile == None:
			return
		
		# mask icon png
		q = QLabel()
		q.setParent(self.editPane)
		pf = os.path.abspath(fbxfile.lower().replace(".fbx",".gif"))
		if os.path.exists(pf):
			m = QMovie(pf)
		else:
			m = QMovie("arttool/noicon.png")
		q.setMovie(m)
		m.start()
		q.setScaledContents(True)
		q.setGeometry(0, 10, 64, 64)
		q.show()

		# mask file name
		q = QLabel(fbxfile[2:])
		q.setParent(self.editPane)
		q.setGeometry(66, 44, 600, 36)
		q.setFont(QFont( "Arial", 14, QFont.Bold ))
		q.setToolTip("This is a tip.\nHopefully on two\nlines.")
		q.show()
		
		# buttons
		b = QPushButton("BUILD")
		b.setParent(self.editPane)
		b.setGeometry(66, 10, 64, 32)
		q.setFont(QFont( "Arial", 14, QFont.Bold ))
		b.pressed.connect(lambda: self.onBuild())
		b.show()
		
		# Tabbed Panel
		tabs = QTabWidget(self.editPane)
		tabs.setGeometry(0, 100, PANE_WIDTH, 600)
		
		# mask meta data fields
		tab1 = QWidget()
		y = 10
		dy = 40
		self.paneWidgets = dict()
		for field in MASK_UI_FIELDS:
			w = self.createLabelWidget(tab1, MASK_UI_FIELDS[field], field, y, field in ["uuid"])
			self.paneWidgets[field] = w
			y += dy
		tab1.setAutoFillBackground(True)
		tabs.addTab(tab1, "Mask Meta Data")
		
		
		
		# additions 
		tab2 = QWidget()
		y = 10
		dy = 40
		self.createLabelWidget(tab2, "Mask Build Additions", None, y)
		y += dy
		
		# make a list widget
		self.addslist = QListWidget()
		if "additions" in self.metadata:
			additions = self.metadata["additions"]
			idx = 0
			for addition in additions:
				self.addslist.addItem(addition["type"] + " : " + addition["name"])
				self.addslist.item(idx).setFont(QFont( "Arial", 12, QFont.Bold ))
				idx += 1
		#self.addslist.itemClicked.connect(lambda: self.onFbxClicked())
		self.addslist.setParent(tab2)
		self.addslist.setGeometry(10,y, PANE_WIDTH - 20, 400)
		y += 410
		
		# buttons for additons
		x = 10
		b = QPushButton("Add")
		b.setParent(tab2)
		b.setGeometry(x, y, 75, 30)
		b.pressed.connect(lambda: self.onAddAddition())
		x += 85
		b = QPushButton("Edit")
		b.setParent(tab2)
		b.setGeometry(x, y, 75, 30)
		b.pressed.connect(lambda: self.onEditAddition())
		x += 85
		b = QPushButton("Del")
		b.setParent(tab2)
		b.setGeometry(x, y, 75, 30)
		b.pressed.connect(lambda: self.onDelAddition())
		x += 85
		b = QPushButton("Up")
		b.setParent(tab2)
		b.setGeometry(x, y, 75, 30)
		b.pressed.connect(lambda: self.onMoveUpAddition())
		x += 85
		b = QPushButton("Down")
		b.setParent(tab2)
		b.setGeometry(x, y, 75, 30)
		b.pressed.connect(lambda: self.onMoveDownAddition())
		
		tab2.setAutoFillBackground(True)
		tabs.addTab(tab2, "Additions")
		
		tabs.show()
		
		
		
	# --------------------------------------------------
	# saveCurrentMetadata
	# --------------------------------------------------
	def saveCurrentMetadata(self):
		if self.metadata:
			fbxfile = self.fbxfiles[self.currentFbx]
			metafile = getMetaFileName(fbxfile)
			writeMetaData(metafile, self.metadata)
	
	# --------------------------------------------------
	# WIDGET SIGNALS CALLBACKS
	# --------------------------------------------------
	
	# FBX file clicked in list
	def onFbxClicked(self):
		self.saveCurrentMetadata()
		self.currentFbx = self.fbxlist.currentRow()
		fbxfile = self.fbxfiles[self.currentFbx]
		self.metadata = createGetMetaData(fbxfile)
		self.updateFbxColorIcon()
		self.createMaskEditPane(fbxfile)
		
	# text field changed
	def onTextFieldChanged(self, text, field):
		self.metadata[field] = text
		if critical(field) and len(text) == 0:
			self.paneWidgets[field].setStyleSheet("border: 1px solid #FF0000;")
		elif desired(field) and len(text) == 0:
			self.paneWidgets[field].setStyleSheet("border: 1px solid #FF7F50;")
		else:
			self.paneWidgets[field].setStyleSheet("border: 0px;")
		self.updateFbxColorIcon()
			
	# checkbox changed
	def onCheckboxChanged(self, state, field):
		if state == 0:
			self.metadata[field] = False
		else:
			self.metadata[field] = True
		self.updateFbxColorIcon()
		
	# texsize changed
	def onTextureSizeChanged(self, state, field):
		self.metadata[field] = int(TEXTURE_SIZES[state])
		
	# called before exit
	def finalCleanup(self):
		self.saveCurrentMetadata()
		metafile = "./.art/config.meta"
		geo = self.geometry()
		self.config["x"] = geo.x()
		self.config["y"] = geo.y()
		writeMetaData(metafile, self.config)

	# build
	def onBuild(self):
		fbxfile = self.fbxfiles[self.currentFbx]
		
		for line in mmImport(fbxfile, self.metadata):
			self.outputWindow.append(line)
		
		jsonfile = jsonFromFbx(fbxfile)
		if self.metadata["depth_head"]:
			# material
			kvp = { "type":"material", 
					"name":"depth_head_mat", 
					"effect":"effectDefault", 
					"depth-only":True }			
			for line in maskmaker("addres", kvp, [jsonfile]):
				self.outputWindow.append(line)
			# model
			kvp = { "type":"model", 
					"name":"depth_head_mdl", 
					"mesh":"meshHead", 
					"material":"depth_head_mat" }			
			for line in maskmaker("addres", kvp, [jsonfile]):
				self.outputWindow.append(line)
			# part
			kvp = { "type":"model", 
					"name":"depth_head", 
					"resource":"depth_head_mdl" }			
			for line in maskmaker("addpart", kvp, [jsonfile]):
				self.outputWindow.append(line)
		
		# DEPS TEST
		#deps = mmDepends(fbxfile)
		#dirname = os.path.dirname(fbxfile)
		#for d in deps:
		#	print(os.path.abspath(os.path.join(dirname, d)))
		
	def onAddAddition(self):
		addn = NewAdditionDialog.go_modal(self)
		if addn:
			if "additions" not in self.metadata:
				self.metadata["additions"] = list()
			self.metadata["additions"].append(addn)
			idx = self.addslist.count()
			self.addslist.addItem(addn["type"] + " : " + addn["name"])
			self.addslist.item(idx).setFont(QFont( "Arial", 12, QFont.Bold ))

	def onEditAddition(self):
		idx = self.addslist.currentRow()
		if idx >= 0:
			addn = AdditionDialog.go_modal(self, self.metadata["additions"][idx])
			if addn:
				self.addslist.item(idx).setText(addn["type"] + " : " + addn["name"])
				self.metadata["additions"][idx] = addn

	def onDelAddition(self):
		idx = self.addslist.currentRow()
		if idx >= 0:
			del self.metadata["additions"][idx]
			i = self.addslist.takeItem(idx)
			i = None

	def onMoveUpAddition(self):
		idx = self.addslist.currentRow()
		if idx > 0:
			self.addslist.insertItem(idx - 1, self.addslist.takeItem(idx))
			self.addslist.setCurrentRow(idx - 1)
			self.metadata["additions"].insert(idx - 1, self.metadata["additions"].pop(idx))

	def onMoveDownAddition(self):
		idx = self.addslist.currentRow()
		if idx >= 0 and self.addslist.count() > 1 and idx < (self.addslist.count() - 1):
			self.addslist.insertItem(idx+1, self.addslist.takeItem(idx))
			self.addslist.setCurrentRow(idx+1)
			self.metadata["additions"].insert(idx+1, self.metadata["additions"].pop(idx))
			
		
		
		