from utilities import docker
from utilities import node
from utilities import dune_error
from utilities import dune_node_not_found
from args import arg_parser
from manifest import manifest

if __name__ == '__main__':
   parser = arg_parser()

   dockr = docker()

   args = parser.parse()

   man = manifest()
   man.read_manifest()

   try:
      if args.start != None:
         dockr.start_node( node(args.start, 'hello'), args.producer, not args.api )

      if args.destroy_container:
         dockr.destroy()

      if args.stop != None:
         dockr.stop_node( node(args.stop, 'hello') )

      if args.monitor != None:
         dockr.monitor( node(args.monitor, 'hello') )

      if args.export_node != None:
         dockr.export_node( node(args.export_node[0], 'hello'), args.export_node[1])
      
      if args.import_node != None:
         dockr.import_node( args.import_node[0], node(args.import_node[1], "hello") )

   except KeyboardInterrupt:
      pass
   except dune_node_not_found as err:
      print('Node not found ['+err.name()+']')