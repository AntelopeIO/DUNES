from dune import dune
from dune import node
from dune import dune_error
from dune import dune_node_not_found
from args import arg_parser

if __name__ == '__main__':
   parser = arg_parser()

   dune_sys = dune()

   if parser.is_forwarding():
      dune_sys.execute_cmd(parser.get_forwarded_args())
   else:
      args = parser.parse()

      try:
         if args.start != None:
            n = None
            if len(args.start) == 1:
               n = node(args.start[0])
            else:
               n = node(args.start[0], args.start[1])
            dune_sys.start_node(n)
         
         elif args.remove != None:
            dune_sys.remove_node( node(args.remove) )

         elif args.destroy_container:
            dune_sys.destroy()
         
         elif args.stop_container:
            dune_sys.stop_container()
         
         elif args.start_container:
            dune_sys.start_container()

         elif args.stop != None:
            dune_sys.stop_node( node(args.stop) )
         
         elif args.list:
            dune_sys.list_nodes()
         
         elif args.simple_list:
            dune_sys.list_nodes(True)

         elif args.set_active != None:
            dune_sys.set_active( node(args.set_active) )

         elif args.monitor:
            dune_sys.monitor()

         elif args.export_node != None:
            dune_sys.export_node( node(args.export_node[0]), args.export_node[1])
         
         elif args.import_node != None:
            dune_sys.import_node( args.import_node[0], node(args.import_node[1]) )

         elif args.import_dev_key != None: 
            dune_sys.import_key(args.import_dev_key)
         
         elif args.create_key:
            print(dune_sys.create_key())

         elif args.create_account != None:
            if len(args.create_account) > 1:
               dune_sys.create_account(args.create_account[0], args.create_account[1])
            else:
               dune_sys.create_account(args.create_account[0], None)

         elif args.cmake_build != None:
            if len(args.build) > 1:
               dune_sys.build_cmake_proj(args.build[0], args.build[1].split())
            else:
               dune_sys.build_cmake_proj(args.build[0], [])

         elif args.other_build != None:
            if len(args.build) > 1:
               dune_sys.build_other_proj(args.build[0], args.build[1].split())
            else:
               dune_sys.build_other_proj(args.build[0], [])

      except KeyboardInterrupt:
         pass
      except dune_node_not_found as err:
         print('Node not found ['+err.name()+']')
      except dune_error as err:
         print("Internal Error")