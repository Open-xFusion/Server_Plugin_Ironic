=================
python-ibmcclient
=================

python-ibmcclient is a Python library to communicate with `iBMC`
based systems.

The goal of the library is to be extremely simple, small, have as few
dependencies as possible and be very conservative when dealing with BMCs
by access HTTP REST API provided by `iBMC` based systems.

Currently, the scope of the library has been limited to supporting
`OpenStack Ironic ibmc driver`

Requirements
============

Python 2.7 and 3.4+

Installation
------------

From PyPi:

.. code-block:: bash

   $ pip install python-ibmcclient


or

.. code-block:: bash

   $ easy_install python-ibmcclient


Or from source:

.. code-block:: bash

   $ python setup.py install

Getting Started
---------------

Please follow the `Installation`_ and then run the following:


.. code-block:: python

    from __future__ import print_function
    from pprint import pprint

    import ibmc_client
    from ibmc_client import constants

    # ibmc server
    address = "https://example.ibmc.com"
    # credential
    username = "username"
    password = "password"
    # disable certification verify
    verify = False

    with ibmc_client.connect(address, username, password, verify) as client:
        # get system
        system = client.system.get()
        print('Power State: ')
        pprint(system.power_state)

        print('Boot Sequence: ')
        pprint(system.boot_sequence)

        print('Boot Source Override:' )
        pprint(system.boot_source_override)

        # reset system
        client.system.reset(constants.RESET_FORCE_RESTART)

        # set boot source override
        client.system.set_boot_source(constants.BOOT_SOURCE_TARGET_PXE,
                                      constants.BOOT_SOURCE_MODE_BIOS,
                                      constants.BOOT_SOURCE_ENABLED_ONCE)

