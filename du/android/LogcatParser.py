from collections import namedtuple
import datetime
import logging


LogcatMessage = namedtuple('Entry', 'pid, tag, time, level, message')

LOGCAT_LEVEL_VERBOSE, \
LOGCAT_LEVEL_DEBUG, \
LOGCAT_LEVEL_INFO, \
LOGCAT_LEVEL_WARNING, \
LOGCAT_LEVEL_ERROR, \
LOGCAT_LEVEL_FATAL = range(6)

LOGCAT_LEVEL_MAP = {
    'V' : LOGCAT_LEVEL_VERBOSE,
    'D' : LOGCAT_LEVEL_DEBUG,
    'I' : LOGCAT_LEVEL_INFO,
    'W' : LOGCAT_LEVEL_WARNING,
    'E' : LOGCAT_LEVEL_ERROR,
    'F' : LOGCAT_LEVEL_FATAL
}

INVERSE_LOGCAT_LEVEMAP = {
    v : k for k, v in LOGCAT_LEVEL_MAP.items()
}

logger = logging.getLogger(__name__)

def parseTimeDate(line):
    tokens = line.split(' ')

    if len(tokens) < 2:
        return None

    # Parse time
    dateTokens = tokens[0].split('-')

    if len(dateTokens) == 2:
        monthDayTokens = tokens[0].split('-')

        if len(monthDayTokens) == 2:
            try:
                month = int(monthDayTokens[0])

                day = int(monthDayTokens[1])

            except ValueError:
                return None
        else:
            return None

        year = datetime.datetime.now().year

    else:
        return None

    time = tokens[1].split(':')

    if len(time) != 3:
        return None

    try:
        hour = int(time[0])

        minute = int(time[1])

        secondMillisecondTokens = time[2].split('.')

        if len(secondMillisecondTokens) != 2:
            return None

        second = int(secondMillisecondTokens[0])

        millisecond = int(secondMillisecondTokens[1])

    except ValueError:
        return None

    return datetime.datetime(day=day, month=month, year=year, hour=hour, minute=minute, second=second, microsecond=millisecond * 1000)

def parseLine(line):
    line = line.rstrip()

    if line.startswith('--------- beginning of'):
        return None

    # Parse time and date
    timeDate = parseTimeDate(line)

    if not timeDate:
        logger.error('Could not parse time/date for message %r' % line)

        return None

    # Parse level
    tagIndex = line.find('/')

    if tagIndex == -1 or tagIndex == 0:
        print('Could not parse tag/level for message %r' % line)
        return None

    levelStr = line[tagIndex - 1]


    if levelStr not in LOGCAT_LEVEL_MAP:
        logger.error('Could not parse level of message %r' % line)
        return None

    level = LOGCAT_LEVEL_MAP[levelStr]

    # Parse message
    messageBeginIndex = line.find('):')

    if messageBeginIndex == -1:
        print('Could not parse message content for message %r' % line)
        return None

    message = line[messageBeginIndex + 3:]

    # Parse pid
    pidBeginIndex = line.rfind('(', 0, messageBeginIndex)

    if pidBeginIndex == -1:
        logger.error('Could not parse PID of message %r' % line)
        return None

    try:
        pid = int(line[pidBeginIndex + 1:].split(')')[0])

    except ValueError:
        logger.error('Could not parse PID of message %r' % line)
        return None

    # Parse tag
    tagBegin = line.rfind('/', 0, pidBeginIndex)

    if tagBegin == -1:
        logger.error('Could not parse tag of message %r' % message)
        return None

    tag = line[tagBegin + 1:pidBeginIndex].rstrip()

    return LogcatMessage(pid, tag, timeDate, level, message)

def parseStream(stream, callbacks):
    if not isinstance(callbacks, list):
        callbacks = [callbacks, ]

    for lineNumber, line in enumerate(stream):
        message = parseLine(line)

        if message:
            for callback in callbacks:
                if not callback(lineNumber, message):
                    break

def parseFile(path, callback):
    with open(path, 'rb') as fileObj:
        return parseStream(fileObj, callback)
