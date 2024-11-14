Service Provider Implementation
===============================

A site must provide its own service provider implementation. The
ServiceProvider API is defined in the py:module:`serviceprovider` module.
Exceptions are defined in the py:module:`spexception` module.

The ServiceProvider API breaks down the actions required by an AMIE packet into
separate tasks. The state of tasks is stored in object defined in the
py:module:`taskstatus` module.

The remaining modules documented here define classes that encapsulate
parameters passed to the ServiceProvider API. These are all subclasses of
py:class:`AMIEParmDescAware`, which simplifies parameter filtering, conversion,
and documentation.


.. autosummary::
   :toctree: generated

   serviceprovider
   spexception
   taskstatus
   account
   allocation
   grant
   organization
   person
   project
   user
