Dashboard panel for ``aiohttp`` applications
============================================


Features
********

- Realtime user interface
- Viewing HTTP activity 
- Viewing WebSocket activity 

Install
*******

.. code-block:: shell
        
    pip install aiohttp_dashboard

Setup
*****

.. code-block:: python
        
    import aiohttp_dashboard

    application = ...
    
    aiohttp_dashboard.setup('<name>', application)


The dashboard is available at ``/<name>``
