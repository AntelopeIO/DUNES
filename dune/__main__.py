from dune import dune
from dune import node
from dune import dune_error
from dune import dune_node_not_found
from args import arg_parser

if __name__ == '__main__':
   parser = arg_parser()

   dune_sys = dune()

   args = parser.parse()

   try:
      if args.start != None:
         n = None
         if len(args.start) == 1:
            n = node(args.start[0])
         else:
            n = node(args.start[0], args.start[1])
         dune_sys.start_node( n, args.producer, not args.api )

      if args.destroy_container:
         dune_sys.destroy()

      if args.stop != None:
         dune_sys.stop_node( node(args.stop) )
      
      if args.list:
         dune_sys.list_nodes()

      if args.set_active != None:
         dune_sys.set_active( node(args.set_active) )

      if args.monitor != None:
         dune_sys.monitor( node(args.monitor) )

      if args.export_node != None:
         dune_sys.export_node( node(args.export_node[0]), args.export_node[1])
      
      if args.import_node != None:
         dune_sys.import_node( args.import_node[0], node(args.import_node[1]) )

      if args.import_dev_key != None: 
         dune_sys.import_key(args.import_dev_key)
      
      if args.create_key:
         print(dune_sys.create_key())

      if args.create_account != None:
         if len(args.create_account) > 1:
            dune_sys.create_account(args.create_account[0], args.create_account[1])
         else:
            dune_sys.create_account(args.create_account[0], None)

   except KeyboardInterrupt:
      pass
   except dune_node_not_found as err:
      print('Node not found ['+err.name()+']')