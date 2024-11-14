# amiemediator
A tool for mediating interactions between AMIE and a local service provider.

The XSEDE/amieclient package is a python library for the AMIE REST API. It
defines all data packets and low-level messaging methods, but leaves all
higher-level and back-end processing tasks to the local service provider.

The NCAR/amiemediator package attempts to simplify the implementation of these
other tasks by providing a back-end ServiceProvider API and a configurable
daemon that handles all interactions with the central AMIE server. The API
tries to make as few assumptions as possible about the nature of the back-end
service provider. The ServiceProvider implementation is expected to be provided
by the local site as python modules that are resolved as run-time. See
src/serviceprovider.py for details.

The daemon program is bin/amie; this program mediates between the AMIE server
and the local service provider; specifically, it retrieves AMIE packets from
the AMIE server, and for each packet it triggers a set of operations on the
service provider using the service provider API.
    
When an operation cannot be completed immediately, the service provider will
create a "task" object. The "amie" program will automatically monitor the
status of each task until all work for the packet is complete and a reply can
be sent back to the AMIE server.

Whenever the state of a task changes, "amie" writes/updates a "snapshot" file
that captures the relevant state of the packet as readable text. All snapshot
files are written to a directory identified in the "amie" configuration file
("snapshot_dir"). When work for a packet is complete, all related data is
destroyed and the corresponding snapshot file is removed. The amiemediator
package includes a command-line utility, bin/viewpackets, that monitors and
displays the contents of the snapshot directory.

An additional program is provided in the package: bin/test-scenario. This
program initializes an AMIE test scenario as described in the *AMIE API Testing*
document.


