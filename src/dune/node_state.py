import sys
#from typing import NamedTuple


class node_state:
    """A simple class for reporting node state."""

    name: str
    is_active: bool
    is_running: bool
    http: str
    p2p: str
    ship: str


    # pylint: disable=too-many-arguments
    def __init__(self, name, is_active, is_running, http, p2p, ship):
        self.name=name
        self.is_active=is_active
        self.is_running=is_running
        self.http=http
        self.p2p=p2p
        self.ship=ship


    def __str__(self):
        active_str='inactive'
        if self.is_active:
            active_str='active'
        running_str='halted'
        if self.is_running:
            running_str='running'
        return f"{self.name}, {active_str}, {running_str}, {self.http}, {self.p2p}, {self.ship}"


    def string(self, file=sys.stdout, sep=',', simple=True):
        active_str='N'
        if self.is_active:
            active_str='Y'
        running_str='N'
        if self.is_running:
            running_str='Y'
        if simple:
            return f"{self.name}{sep}{active_str}{sep}{running_str}{sep}{self.http}{sep}{self.p2p}{sep}{self.ship}"
        return f"{self.name}\t\t {sep}    {active_str}\t   {sep}    {running_str}     {sep} {self.http} {sep} {self.p2p} {sep} {self.ship}"
