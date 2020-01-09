Dashboard panel for ``aiohttp`` applications
============================================


Features
********

- Realtime user interface
- Viewing HTTP activity
- Viewing WebSocket activity
- Mobile frendly
- Used Vuejs + Bootstrap for building UI


Install
*******

.. code-block:: shell
    
    pip install aiohttp_dashboard


Requirments
***********
- python 3.5.3
- aiohttp 3.*
- mongodb 3.6.*

Setup
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


The dashboard is available at ``/dashboard_prefix``


Screenshots
***********

[![N|Solid](./images/desctop-overview.png)]