def handle_args(args):
    if args.hello:
        print('Hello from DUNE plugin!')

def add_parsing(parser):
    parser.add_argument('--hello', action='store_true',
                                  help='outputs "Hello World"')
