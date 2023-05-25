import os   # path
import sys  # sys.exit()
import importlib.util

from args import arg_parser
from args import parse_optional
import version_selector
from docker import docker_error

from version import version_full
from dunes import dunes
from dunes import dunes_error
from dunes import dunes_node_not_found
from dunes import node


def handle_version():
    print("DUNES v" + version_full())


def handle_simple_args():
    # Handle args that do not require docker started up
    if args.version is True:
        handle_version()
        sys.exit(0)
    if args.version_short is True:
        print(version_full())
        sys.exit(0)


def load_module(absolute_path):
    module_name, _ = os.path.splitext(os.path.split(absolute_path)[-1])
    module_root = os.path.dirname(absolute_path)

    sys.path.append(module_root)
    spec = importlib.util.spec_from_file_location(module_name, absolute_path)
    py_mod = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(py_mod)
        return py_mod
    # Any exception here should be trapped and None returned.
    #   pylint: disable=bare-except
    except:
        return None


def load_all_modules_from_dir(plugin_dir):
    loaded_modules = []

    if not os.path.exists(plugin_dir):
        return loaded_modules

    for subdir in os.listdir(plugin_dir):
        subdir_path = os.path.join(plugin_dir, subdir)
        if not os.path.isdir(subdir_path):
            continue

        main_py = os.path.join(subdir_path, 'main.py')
        if not os.path.exists(main_py):
            print(f'main.py not found in {subdir_path}')
            continue

        loaded_module = load_module(main_py)
        if not loaded_module:
            print(f'Could not load {main_py}')
            continue
        if not hasattr(loaded_module, 'handle_args'):
            print('Plugin ' + main_py + ' does not have handle_args() method')
            continue
        if not hasattr(loaded_module, 'add_parsing'):
            print('Plugin ' + main_py + ' does not have add_parsing() method')
            continue

        loaded_modules.append(loaded_module)

    return loaded_modules


if __name__ == '__main__':

    parser = arg_parser()

    current_script_path = os.path.abspath(__file__)
    current_script_dir = os.path.dirname(current_script_path)
    pluggin_dir = os.path.join(os.path.split(current_script_dir)[0], 'plugin')

    modules = []
    for module in load_all_modules_from_dir(pluggin_dir):
        try:
            module.add_parsing(parser.get_parser())
            modules.append(module)
        # Any exception here should be trapped here and the user notified before continuing.
        #   pylint: disable=bare-except
        except:
            print(f"Can't load module {module}")
            continue

    args = parser.parse()

    handle_simple_args()

    dunes_sys = dunes(args)

    for module in modules:
        if hasattr(module, 'set_dunes'):
            module.set_dunes(dunes_sys)

    try:
        if parser.is_forwarding():
            dunes_sys.execute_interactive_cmd(parser.get_forwarded_args())
        else:
            WAS_REMAINDER_ARGS_USED = False

            if args.start is not None:
                n: object = None
                if args.config is None:
                    n = node(args.start[0])
                elif len(args.config) == 1:
                    cfg_temp = args.config[0]
                    if not os.path.exists(cfg_temp):
                        parser.exit_with_help_message("--config: config.ini unknown path\n",
                                                       "bad value: ", cfg_temp)
                    if os.path.isdir(cfg_temp):
                        cfg_temp = os.path.join(cfg_temp, "config.ini")
                    if os.path.split(cfg_temp)[1] != "config.ini":
                        parser.exit_with_help_message("--config: config must either be a config.ini"
                                                      "file or a path containg one\n"
                                                      "bad value: ", cfg_temp)
                    if not os.path.exists(cfg_temp):
                        parser.exit_with_help_message("--config: config.ini file must exist\n"
                                                      "bad value: ", cfg_temp)
                    n = node(args.start[0], dunes_sys.docker.abs_host_path(cfg_temp))
                else:
                    parser.exit_with_help_message("--start / --config error")
                dunes_sys.start_node(n)

            elif args.config is not None:
                parser.exit_with_help_message("--config without --start")

            elif args.remove is not None:
                dunes_sys.remove_node(node(args.remove))

            elif args.destroy_container:
                dunes_sys.destroy()

            elif args.stop_container:
                dunes_sys.stop_container()

            elif args.start_container:
                dunes_sys.start_container()

            elif args.stop is not None:
                dunes_sys.stop_node(node(args.stop))

            elif args.list:
                dunes_sys.list_nodes()

            elif args.simple_list:
                dunes_sys.list_nodes(True)

            elif args.set_active is not None:
                dunes_sys.set_active(node(args.set_active))

            elif args.get_active:
                print(dunes_sys.get_active())

            elif args.monitor:
                dunes_sys.monitor()

            elif args.export_wallet:
                dunes_sys.export_wallet()

            elif args.import_wallet is not None:
                dunes_sys.import_wallet(args.import_wallet)

            elif args.export_node is not None:
                dunes_sys.export_node(node(args.export_node[0]),
                                      args.export_node[1])

            elif args.import_node is not None:
                dunes_sys.import_node(args.import_node[0],
                                      node(args.import_node[1]))

            elif args.import_dev_key is not None:
                dunes_sys.import_key(args.import_dev_key)

            elif args.create_key:
                print(dunes_sys.create_key())

            elif args.create_account is not None:
                if len(args.create_account) > 2:
                    dunes_sys.create_account(args.create_account[0],
                                             args.create_account[1],
                                             args.create_account[2],
                                             args.create_account[3])
                elif len(args.create_account) > 1:
                    dunes_sys.create_account(args.create_account[0],
                                             args.create_account[1])
                else:
                    dunes_sys.create_account(args.create_account[0])

            elif args.system_newaccount is not None:
                commands, WAS_REMAINDER_ARGS_USED = parse_optional(args.remainder)

                if (len(args.system_newaccount) > 4
                    or (WAS_REMAINDER_ARGS_USED
                        and len(args.system_newaccount) < 4)):
                    parser.exit_with_help_message("--system-newaccount has invalid arguments\n")
                if WAS_REMAINDER_ARGS_USED:
                    dunes_sys.system_newaccount(*args.system_newaccount, commands)
                else:
                    dunes_sys.system_newaccount(*args.system_newaccount)

            elif args.create_cmake_app is not None:
                dunes_sys.init_project(args.create_cmake_app[0],
                                       dunes_sys.docker.abs_host_path(
                                          args.create_cmake_app[1]), True)

            elif args.create_bare_app is not None:
                dunes_sys.init_project(args.create_bare_app[0],
                                       dunes_sys.docker.abs_host_path(
                                          args.create_bare_app[1]),
                                       False)

            elif args.cmake_build is not None:
                commands, WAS_REMAINDER_ARGS_USED = parse_optional(args.remainder)
                dunes_sys.build_cmake_proj(args.cmake_build[0], commands)

            elif args.ctest is not None:
                commands, WAS_REMAINDER_ARGS_USED = parse_optional(args.remainder)
                dunes_sys.ctest_runner(args.ctest[0], commands)

            elif args.gdb is not None:
                commands, WAS_REMAINDER_ARGS_USED = parse_optional(args.remainder)
                dunes_sys.gdb(args.gdb[0], commands)

            elif args.deploy is not None:
                dunes_sys.deploy_contract(
                    dunes_sys.docker.abs_host_path(args.deploy[0]),
                    args.deploy[1])

            elif args.set_bios_contract is not None:
                dunes_sys.deploy_contract(
                    '/app/reference-contracts/build/contracts/eosio.bios',
                    args.set_bios_contract)

            elif args.set_core_contract is not None:
                dunes_sys.deploy_contract(
                    '/app/reference-contracts/build/contracts/eosio.system',
                    args.set_core_contract)

            elif args.set_token_contract is not None:
                dunes_sys.deploy_contract(
                    '/app/reference-contracts/build/contracts/eosio.token',
                    args.set_token_contract)

            elif args.bootstrap_system:
                dunes_sys.bootstrap_system(False)

            elif args.bootstrap_system_full is not None:
                if len(args.bootstrap_system_full) > 3:
                    parser.exit_with_help_message("--bootstrap-system-full should have at most 3 arguments\n")
                else:
                    dunes_sys.bootstrap_system(True, *args.bootstrap_system_full)

            elif args.activate_feature is not None:
                dunes_sys.activate_feature(args.activate_feature, True)

            elif args.list_features:
                for f in dunes_sys.features():
                    print(f)

            elif args.send_action is not None:
                dunes_sys.send_action(args.send_action[1], args.send_action[0],
                                      args.send_action[2], args.send_action[3])

            elif args.get_table is not None:
                dunes_sys.get_table(args.get_table[0], args.get_table[1],
                                    args.get_table[2])

            elif args.upgrade:
                dunes_sys.docker.upgrade()

            elif args.leap:
                if args.leap == '-1':
                    args.leap = version_selector.get_version("Leap")
                dunes_sys.execute_cmd(['sh', 'bootstrap_leap.sh', args.leap])

            elif args.cdt:
                if args.cdt == '-1':
                    args.cdt = version_selector.get_version("CDT")
                dunes_sys.execute_cmd(['sh', 'bootstrap_cdt.sh', args.cdt])

            elif args.version_all:
                handle_version()
                dunes_sys.execute_cmd(['apt', 'list', 'leap'], colors=True)
                dunes_sys.execute_cmd(['apt', 'list', 'cdt'], colors=True)

# Integration with antler-proj begin ----------------------------------------------------------------------

            elif args.create_project:
                if len(args.create_project) < 2 or len(args.create_project) > 3:
                    parser.exit_with_help_message("--create_project: invalid number of arguments")
                else:
                    dunes_sys.create_project(*args.create_project)
            elif args.add_app:
                if len(args.add_app) < 3 or len(args.add_app) > 5:
                    parser.exit_with_help_message("--add-app: invalid number of arguments")
                else:
                    dunes_sys.add_app(*args.add_app)
            elif args.add_lib:
                if len(args.add_lib) < 3 or len(args.add_lib) > 5:
                    parser.exit_with_help_message("--add-lib: invalid number of arguments")
                else:
                    dunes_sys.add_lib(*args.add_lib)
            elif args.add_dep:
                if len(args.add_dep) < 3 or len(args.add_dep) > 6:
                    parser.exit_with_help_message("--add-dep: invalid number of arguments")
                else:
                    dunes_sys.add_dep(*args.add_dep)
            elif args.update_app:
                if len(args.update_app) < 3 or len(args.update_app) > 5:
                    parser.exit_with_help_message("--update-app: invalid number of arguments")
                else:
                    dunes_sys.update_app(*args.update_app)
            elif args.update_lib:
                if len(args.update_lib) < 3 or len(args.update_lib) > 5:
                    parser.exit_with_help_message("--update-lib: invalid number of arguments")
                else:
                    dunes_sys.update_lib(*args.update_lib)
            elif args.update_dep:
                if len(args.update_dep) < 3 or len(args.update_dep) > 5:
                    parser.exit_with_help_message("--update-dep: invalid number of arguments")
                else:
                    dunes_sys.update_dep(*args.update_dep)
            elif args.remove_app:
                dunes_sys.remove_app(*args.remove_app)

            elif args.remove_lib:
                dunes_sys.remove_lib(*args.remove_lib)

            elif args.remove_dep:
                dunes_sys.remove_dep(*args.remove_dep)

            elif args.build_project:
                dunes_sys.build_project(args.build_project[0])

            elif args.clean_build_project:
                dunes_sys.build_project(args.clean_build_project[0], True)

            elif args.validate:
                dunes_sys.validate_project(args.validate[0])

            elif args.populate:
                dunes_sys.populate_project(args.populate[0])

# Integration with antler-proj end ----------------------------------------------------------------------

            else:
                for module in modules:
                    module.handle_args(args)

            if args.remainder and WAS_REMAINDER_ARGS_USED is False:
                print('Warning: following arguments were possibly unused: ' + str(args.remainder))

    except KeyboardInterrupt:
        pass
    except dunes_node_not_found as err:
        print('Node not found [' + err.name() + ']', file=sys.stderr)
        sys.exit(1)
    except dunes_error as err:
        print("Internal Error", file=sys.stderr)
        sys.exit(1)
    except docker_error as err:
        print("Docker Error", file=sys.stderr)
        sys.exit(1)
