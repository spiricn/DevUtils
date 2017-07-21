from collections import namedtuple
import logging
import re

from du.android.LogcatParser import parseTimeDate


logger = logging.getLogger(__name__.split('.')[-1])

ParsedPoint = namedtuple('ParsedPoint', 'message,time')

def timeDeltaMs(a, b):
    return int((b - a).total_seconds() * 1000.0)

class Logan:
    def __init__(self, points):
        self._points = []

        for i in points:
            logger.debug('Adding point: %r' % i)
            self._points.append(re.compile(i))

        logger.debug('-' * 10)

        self._parsed = []

    def parse(self, stream, outputStream):
        started = False

        for line in stream.readlines():
            res = self._parseLine(line)
            if not res:
                continue

            index, parsedPoint = res

            stop = False
            if index == 0:
                self._parsed = []
                started = True
            elif index == len(self._points) - 1:
                logger.debug('detected end point')
                stop = True

            self._parsed.append(parsedPoint)

            if stop and started:
                outputStream.write(self._analyseHtml())

            if stop:
                self._parsed = []
                started = False



    def _analyseHtml(self):
        res = '<html><body>\n'

        res += '<table border="1" style="border-collapse:collapse;" cellpadding="10">'

        res += '<tr><th>Message</th><th> Time from start </th><th> Time </th>'
        for idx, point in enumerate(self._parsed):
            res += '<tr>'
            timeFromStartMs = 0
            timeFromPrevMs = 0
            if idx > 0:
                timeFromStartMs = timeDeltaMs(self._parsed[0].time, point.time)
                timeFromPrevMs = timeDeltaMs(self._parsed[idx - 1].time, point.time)

            res += '<td>%s</td><td>%d</td><td>%d</td>' % (point.message, timeFromStartMs, timeFromPrevMs)

            print(point.message, timeFromStartMs, timeFromPrevMs)

            res += '</tr>'

        totalTimeMs = 0
        if len(self._points) >= 2:
            totalTimeMs = timeDeltaMs(self._parsed[0].time, self._parsed[-1].time)
        res += '</table>'

        res += '<table>'
        res += '<tr><td>Total time</td><td>%d</td></tr>' % totalTimeMs
        res += '<tr><td>Points</td><td>%d</td></tr>' % len(self._points)
        res += '</table>'
        res += '</body></html>'

        print('-------')
        print('Total: %d ms' % totalTimeMs)

        return res

    def _parseLine(self, line):
        line = line.rstrip()

        for index, point in enumerate(self._points):
            if point.findall(line):
                timeDate = parseTimeDate(line)
                if not timeDate:
                    logger.error('error parsing time & date: %r' % line)

                return index, ParsedPoint(line, timeDate)
