from du.cgen.Generator import Generator, TYPE_BOOL, TYPE_INT32, TYPE_STRING

class JavaGenerator(Generator):
    TYPE_MAP = {
        TYPE_STRING : 'String',
        TYPE_BOOL : 'boolean',
        TYPE_INT32 : 'int'
    }
    def __init__(self, package, className, params):
        Generator.__init__(self, params)

        self._package = package
        self._className = className

    def generate(self):
        res = ''

        res += '''\
/****************************************
*             DO NOT EDIT               *
* This file was automatically generated *
*****************************************/\n\n'''

        res += 'package %s;\n' % self._package

        res += '\n'

        res += 'final public class %s {\n' % self._className

        for param in self._params:
            res += '    public static final '

            if param.type not in self.TYPE_MAP:
                raise NotImplementedError('Unsupported type: %d' % param.type)

            res += self.TYPE_MAP[param.type] + ' ' + param.name + ' = '

            if param.type == TYPE_STRING:
                res += '"%s"' % param.value
            elif param.type == TYPE_BOOL:
                res += 'true' if param.value else 'false'
            elif param.type == TYPE_INT32:
                res += '%d' % param.value
            else:
                raise RuntimeError('Unsupported type: %d' % param.type)

            res += ';\n\n'

        res += '    public static String getString(){\n'

        res += '        return "[%s]["' % (self._package + '.' + self._className)

        for index, param in enumerate(self._params):

            res += ' + "%s%s=" + %s' % ('' if index == 0 else ' ', param.name, param.name)

        res += ' + "]";\n'
        res += '    }\n'

        res += '}\n'

        return res