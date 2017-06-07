from collections import namedtuple
from threading import Thread, Semaphore


class Ctee:
    Input = namedtuple('Input', 'stream, processor')
    Output = namedtuple('Input', 'stream, transformer')

    def __init__(self):
        self._input = None
        self._outputs = []
        self._thread = None
        self._running = False
        self._sema = Semaphore(0)

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
        if not self._running:
            return

        self._input.stream.close()
        self._thread.join()

    def wait(self):
        while self._running:
            self._sema.acquire()

    def _write(self, stream, data):
        stream.write(data)
        stream.flush()

    def _mainLoop(self):
        try:
            for output in self._outputs:
                self._write(output.stream, output.transformer.getHeader())

            while self._running:
                line = self._input.stream.readline()
                if not line:
                    break

                line = line.rstrip()

                chunks = self._input.processor.getStyle(line)

                self._write(output.stream, output.transformer.onLineStart())

                for output in self._outputs:
                    for chunk, style in chunks:
                        transformedChunk = output.transformer.transform(chunk, style)

                        self._write(output.stream, transformedChunk)

                    self._write(output.stream, '\n')

                self._write(output.stream, output.transformer.onLineEnd())

            for output in self._outputs:
                self._write(output.stream, output.transformer.getTrailer())

        except (IOError, ValueError):
            pass

        self._running = False
        self._sema.release()
