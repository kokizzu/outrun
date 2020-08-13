"""
Modules that implement the local and remote logic of outrun.

The local instance starts an SSH session with the remote machine to launch the remote
instance of outrun along with two TCP tunnels to later expose RPC services. The remote
instance will first ensure that it runs as root (to access chroot), unshares its mounts,
and enables the FUSE kernel module.

To prevent any unwanted programs on either the local or remote machine from connecting
to these services, the local and remote end need to agree on a shared authentication
token. The token is generated by the remote instance and written to stdout, surrounded
by SOH (Start of Header) and STX (Start of Text) control characters. The local instance
proxies all of SSH's stdout to look for and filter this token. The token includes a
checksum that provides some degree of confidence that the remote outrun instance has
correctly started.

Once this handshake has completed, the local instance starts two RPC services:

* Environment service: provides the context for running the command, like working
directory, environment variables, the command itself, and its arguments.
* Local file system service: provides I/O functions to mirror the local file system on
the remote machine.

The remote instance waits for these services to be ready and connects to them through
the previously set up SSH tunnels.

The process of mirroring the local environment can now begin and starts by mounting a
FUSE file system that, in essence, simply forwards all of its I/O calls to the local
file system RPC service. The command to run and its context is then retrieved from the
environment RPC service. A new process is started with the original environment
variables and original command that chroots into the mirrored file system, sets the
working directory and then begins running as normal. All of its stdin, stdout, and
stderr is forwarded over SSH, and all of its file system operations are handled as if
the program was running locally.

Once the program has exited, the remote instance unmounts the file system and exits with
the same exit code as the program. SSH's exit code further propagates this to the local
instance and it too will exit with that same exit code to complete the illusion of the
command having run as normally as possible, just on a different machine.

Any unexpected turn of events, like RPC services failing or the mirrored file system
unexpectedly unmounting before the program has completed, are picked up by the event
queue and result in an immediate shutdown.
"""

from .common import Operations
from .local import LocalOperations
from .remote import RemoteOperations

__all__ = [
    "Operations",
    "LocalOperations",
    "RemoteOperations",
]
