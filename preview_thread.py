from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import pyqtSignal, pyqtSlot
from PIL import Image, ImageDraw, ImageFont
from PIL.ImageQt import ImageQt
import core
import time
from queue import Queue, Empty
import numpy
import os
from copy import copy

class Worker(QtCore.QObject):

  imageCreated = pyqtSignal(['QImage'])

  def __init__(self, parent=None, queue=None):
    QtCore.QObject.__init__(self)
    parent.newTask.connect(self.createPreviewImage)
    parent.processTask.connect(self.process)
    self.core = core.Core()
    self.queue = queue
    self.core.settings = parent.settings
    self.stackedWidget = parent.window.stackedWidget
    self.background = Image.new("RGBA", (1920, 1080),(0,0,0,0))
    self.background.paste(Image.open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"background.png")))
    


  @pyqtSlot(str, list)
  def createPreviewImage(self, components):
    # print('worker thread id: {}'.format(QtCore.QThread.currentThreadId()))
    dic = {
      "components": components,
    }
    self.queue.put(dic)

  @pyqtSlot()
  def process(self):
    try:
      nextPreviewInformation = self.queue.get(block=False)
      while self.queue.qsize() >= 2:
        try:
          self.queue.get(block=False)
        except Empty:
          continue

      width = int(self.core.settings.value('outputWidth'))
      height = int(self.core.settings.value('outputHeight'))
      frame = copy(self.background)
      frame = frame.resize((width,height))

      components = nextPreviewInformation["components"]
      for component in reversed(components):
        #newFrame = Image.alpha_composite(frame,)
        frame = Image.alpha_composite(frame,component.previewRender(self))

      self._image = ImageQt(frame)
      self.imageCreated.emit(QtGui.QImage(self._image))
      
    except Empty:
      True
