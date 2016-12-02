from collections import namedtuple
from threading import Thread
import time


class Ctee:
    Input = namedtuple('Input', 'stream, processor')
    Output = namedtuple('Input', 'stream, transformer')
    
    def __init__(self):
        self._input = None
        self._outputs = []
        self._thread = None
        self._running = False
        
    def setInput(self, stream, processor):
        if self._running:
            raise RuntimeError('Ctee running')
        
        self._input = Ctee.Input(stream, processor)
    
    def addOutput(self, stream, transformer):
        if self._running:
            raise RuntimeError('Ctee running')
        
        self._outputs.append(Ctee.Output(stream, transformer))

    def start(self):
        if self._running:
            raise RuntimeError('Ctee running')
        
        self._running = True
        self._thread = Thread(target=self._mainLoop)
        self._thread.start()
        
    def stop(self):
        if self._running:
            raise RuntimeError('Ctee not running')
        
        self._running = False
        self._thread.join()
        
    def wait(self):
        while self._running:
            time.sleep(0.5)
        
    def _mainLoop(self):
        for output in self._outputs:
            output.stream.write(output.transformer.getHeader())
                
        for line in self._input.stream:
            style = self._input.processor.getStyle(line)
            
            for output in self._outputs:
                output.stream.write(output.transformer.transform(line, style))

        for output in self._outputs:
            output.stream.write(output.transformer.getTrailer())
            
        self._running = False
        
            