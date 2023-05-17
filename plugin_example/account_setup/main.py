class account_setup_plugin:
    _dunes = None

    @staticmethod
    def set_dunes(in_dunes):
        account_setup_plugin._dunes = in_dunes

    @staticmethod
    def create_accounts():
        account_setup_plugin._dunes.create_account('alice')
        account_setup_plugin._dunes.create_account('bob')
        account_setup_plugin._dunes.create_account('cindy')

    @staticmethod
    def deploy_contracts():
        account_setup_plugin._dunes.deploy_contract(
            '/app/reference-contracts/build/contracts/eosio.token',
            'alice')
        account_setup_plugin._dunes.deploy_contract(
            '/app/reference-contracts/build/contracts/eosio.token',
            'bob')
        account_setup_plugin._dunes.deploy_contract(
            '/app/reference-contracts/build/contracts/eosio.token',
            'cindy')


def handle_args(args):
    if args.bootstrap_account:
        print('Starting account bootstrapping')
        account_setup_plugin.create_accounts()
        account_setup_plugin.deploy_contracts()
        print('Created accounts and deployed contracts')


def set_dunes(in_dunes):
    account_setup_plugin.set_dunes(in_dunes)


def add_parsing(parser):
    parser.add_argument('--bootstrap-account', action='store_true',
                        help='Set up 3 example accounts together with their token contracts')
