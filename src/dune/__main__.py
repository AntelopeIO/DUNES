from dune import dune
from dune import node
from dune import dune_error
from dune import dune_node_not_found
from dune import version_full
from args import arg_parser
from args import parse_optional

import os

if __name__ == '__main__':
   parser = arg_parser()

   dune_sys = dune()

   if parser.is_forwarding():
      dune_sys.execute_interactive_cmd(parser.get_forwarded_args())
   else:
      args = parser.parse()

      try:
         if args.start != None:
            n = None
            if len(args.start) == 1:
               n = node(args.start[0])
            else:
               n = node(args.start[0], dune_sys._docker.abs_host_path(args.start[1]))
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
         
         elif args.get_active:
            print(dune_sys.get_active())

         elif args.monitor:
            dune_sys.monitor()

         elif args.export_wallet:
            dune_sys.export_wallet()
         
         elif args.import_wallet != None:
            dune_sys.import_wallet(args.import_wallet)

         elif args.export_node != None:
            dune_sys.export_node( node(args.export_node[0]), args.export_node[1])
         
         elif args.import_node != None:
            dune_sys.import_node( args.import_node[0], node(args.import_node[1]) )

         elif args.import_dev_key != None: 
            dune_sys.import_key(args.import_dev_key)
         
         elif args.create_key:
            print(dune_sys.create_key())

         elif args.create_account != None:
            if len(args.create_account) > 2:
               dune_sys.create_account(args.create_account[0], args.create_account[1], args.create_account[2], args.create_account[3])
            elif len(args.create_account) > 1:
               dune_sys.create_account(args.create_account[0], args.create_account[1])
            else:
               dune_sys.create_account(args.create_account[0])

         elif args.create_cmake_app != None:
            dune_sys.init_project(args.create_cmake_app[0], dune_sys._docker.abs_host_path(args.create_cmake_app[1]), True)

         elif args.create_bare_app != None:
            dune_sys.init_project(args.create_bare_app[0], dune_sys._docker.abs_host_path(args.create_bare_app[1]), False)

         elif args.cmake_build != None:
            dune_sys.build_cmake_proj(args.cmake_build[0], parse_optional(args.remainder))

         elif args.ctest != None:
            dune_sys.ctest_runner(args.ctest[0], parse_optional(args.remainder))
         
         elif args.gdb != None:
            dune_sys.gdb(args.gdb[0], parse_optional(args.remainder))

         elif args.deploy != None:
            dune_sys.deploy_contract(dune_sys._docker.abs_host_path(args.deploy[0]), args.deploy[1])

         elif args.set_bios_contract != None:
            dune_sys.deploy_contract( '/app/reference-contracts/build/contracts/eosio.bios', args.set_bios_contract)
        
         elif args.set_core_contract != None:
            dune_sys.deploy_contract( '/app/reference-contracts/build/contracts/eosio.system', args.set_core_contract)

         elif args.set_token_contract != None:
            dune_sys.deploy_contract( '/app/reference-contracts/build/contracts/eosio.token', args.set_token_contract)
         
         elif args.bootstrap_system:
            dune_sys.bootstrap_system(False)

         elif args.bootstrap_system_full:
            dune_sys.bootstrap_system(True)

         elif args.activate_feature != None:
            dune_sys.activate_feature(args.activate_feature, True)
         
         elif args.list_features:
            for f in dune_sys.features():
               print(f)
            
         elif args.send_action != None:
            dune_sys.send_action(args.send_action[1], args.send_action[0], args.send_action[2], args.send_action[3])
         
         elif args.get_table != None:
            dune_sys.get_table(args.get_table[0], args.get_table[1], args.get_table[2])

         elif args.version:
            print ("DUNE "+version_full())
            
         else:
            print("Unsupported or wrong command")

      except KeyboardInterrupt:
         pass
      except dune_node_not_found as err:
         print('Node not found ['+err.name()+']')
      except dune_error as err:
         print("Internal Error")
