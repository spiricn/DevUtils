import argparse
import sys

from du.ctee.Ctee import Ctee
from du.ctee.processors.LogcatProcessor import LogcatProcessor
from du.ctee.transformers.HtmlTransformer import HtmlTransformer
from du.ctee.transformers.PasstroughTransformer import PasstroughTransformer
from du.ctee.transformers.TerminalTransformer import TerminalTransformer


PROCESSOR_MAP = {
    'logcat' : LogcatProcessor,
}

TRANSFORMER_MAP = {
    'terminal' : TerminalTransformer,
    'passtrough' : PasstroughTransformer,
    'html' : HtmlTransformer
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-stylesheet')
    parser.add_argument('-input')
    parser.add_argument('-processor', help='available processors: %s' % ','.join(PROCESSOR_MAP.keys()))
    parser.add_argument('-outputs', nargs='+', help='list of <output,transformer> pairs; available transformers: %s' % (','.join(TRANSFORMER_MAP.keys())))
    
    args = parser.parse_args()

    if args.stylesheet:
        if args.stylesheet in PROCESSOR_MAP:
            print( PROCESSOR_MAP[args.stylesheet].getDefaultStylesheet() )
            return 0
            
        else:
            print('invalid processor name %r' % args.processor)
            return -1
    
    ctee = Ctee()
    
    inputStream = None
    
    if args.input == '-':
        inputStream = sys.stdin
    else:
        inputStream = open(args.input, 'rb')
        
    if args.processor in PROCESSOR_MAP:
        processor = PROCESSOR_MAP[args.processor]()
    else:
        print('invalid processor name %r' % args.processor)
        
    ctee.setInput(inputStream, processor)
    
    if not args.outputs:
        # Default to terminal output/stdout
        ctee.addOutput(sys.stdout, TerminalTransformer())
    else:
        for i in range(0, len(args.outputs), 2):
            outputStream = args.outputs[i + 0]
            outputTransformerName = args.outputs[i + 1]
            
            if outputStream == '-':
                outputStream = sys.stdout
            else:
                outputStream = open(outputStream, 'wb')
                
            if outputTransformerName in TRANSFORMER_MAP:
                transformer = TRANSFORMER_MAP[outputTransformerName]()
            else:
                raise RuntimeError('Invalid transformer name %r' % outputTransformerName)
                
            ctee.addOutput(outputStream, transformer)
        
    
    ctee.start()
    
    ctee.wait()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
