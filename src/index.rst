.. AMIEMediator documentation master file, created by
   sphinx-quickstart on Wed Sep  4 15:13:26 2024.

AMIEMediator documentation
==========================

The **AMIEMediator** package defines tools for mediating interactions between
AMIE and a local service provider.

The ``XSEDE/amieclient`` package is a python library for the AMIE REST API. It
defines all data packets and low-level messaging methods, but leaves all
higher-level and back-end processing tasks to the local service provider.

The ``NCAR/amiemediator`` package attempts to simplify the implementation of
these other tasks by providing a back-end ServiceProvider API and a configurable
daemon that handles all interactions with the central AMIE server. The API
tries to make as few assumptions as possible about the nature of the back-end
service provider. The ServiceProvider implementation is expected to be provided
by the local site as python modules that are resolved at run-time. See
:doc:`sp_implementation` for details.

.. toctree::
   :maxdepth: 3
   :caption: Contents:
             
   scripts
   api

