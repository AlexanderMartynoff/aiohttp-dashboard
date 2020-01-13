Dashboard panel for ``aiohttp`` applications
============================================


Features
********

- Realtime UI build on top WebSocket
- Viewing HTTP activity
- Viewing WebSocket activity
- Responsive and mobile friendly UI build on top bootstrap 4 and vue.js

Install
*******

.. code-block:: shell
    
    pip install aiohttp_dashboard


Requirments
***********
- python >= 3.5.3
- aiohttp >= 3.0
- mongodb >= 3.6.0

Usage
*****

.. code-block:: python

    import aiohttp_dashboard

    application = create_my_aiohttp_app()
    
    aiohttp_dashboard.setup(
        '/dashboard_prefix',  # URL prefix for dashboard UI
        application,
        {
            # optional configrutaion for mongodb
            # below shows settings by default
            'mongo': {
                'port': 27017,
                'host': 'localhost',
                'database': 'aiohttp_dashboard',
            }
        }
    )


The dashboard index page is available at ``/dashboard_prefix``.

Development
***********

Requirments
-----------
- nodejs >= 4.0.0
- npm >= 3.0.0

Build frontend assets:
----------------------

.. code-block:: bash

    git clone git@github.com:AlexanderMartynoff/aiohttp-dashboard.git

    cd aohttp-dashboard/aohttp_dashboard/assets

    npm run build

Usage demo application as sandbox
---------------------------------

.. code-block:: bash

    cd aohttp-dashboard/aohttp_dashboard

    python sandbox/demo

After build assets and run demo application you can send tests HTPP request and websocket messages with demo site that available on ``/`` path and dashboard UI available on ``/dashboard`` path, for more details see ``aohttp_dashboard/sandbox/demo``.