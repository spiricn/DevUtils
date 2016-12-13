import unittest

from du.ctee.Color import Color
from du.ctee.Style import Style
from du.ctee.transformers.HtmlTransformer import HtmlTransformer
from du.ctee.transformers.TerminalTransformer import TerminalTransformer
from du.ctee.transformers.PasstroughTransformer import PasstroughTransformer


class TerminalTransformerTest(unittest.TestCase):
    def setUp(self):
        pass

    def testBasic(self):
        transformers = (
            ('terminal', TerminalTransformer()),
            ('html', HtmlTransformer()),
            ('passtrough', PasstroughTransformer()),
            )

        for tfName, tf in transformers:
            print('Testing ' + tfName + '...\n')

            colors = (
                ('red', Color.RED),
                ('green', Color.GREEN),
                ('blue', Color.BLUE),
                ('cyan', Color.CYAN),
                ('magenta', Color.MAGENTA),
                ('yellow', Color.YELLOW),
                ('black', Color.BLACK),
                ('white', Color.WHITE))

            print('Foreground test:')
            for name, color in colors:
                print(name + '\t\t. . . ' + tf.transform('[###test###]', Style(fgColor=color)) + ' . . .')
            print('\n')

            print('Background test:')
            for name, color in colors:
                print(name + '\t\t. . . ' + tf.transform('[###test###]', Style(bgColor=color)) + ' . . .')
            print('\n')

            print('Format test:')
            print('bold' + '\t\t\t. . . ' + tf.transform('[###test###]', Style(bold=True)) + ' . . .')
            print('underline' + '\t\t. . . ' + tf.transform('[###test###]', Style(underline=True)) + ' . . .')
            print('both' + '\t\t\t. . . ' + tf.transform('[###test###]', Style(bold=True, underline=True)) + ' . . .')
            print('\n')

            print('Advanced:')
            print('mix' + '\t\t\t. . . ' + tf.transform('[###test###]', Style(bgColor=Color.WHITE, fgColor=Color.BLUE, bold=True, underline=True)) + ' . . .')
