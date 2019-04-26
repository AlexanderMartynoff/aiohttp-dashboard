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
        
    pip install aiohttp_debugger

Setup
*****

.. code-block:: python
        
    import aiohttp_debugger

    application = ...
    
    aiohttp_debugger.setup('/aiohttp_debugger', application)


The dashboard is available at ``<application_url>/aiohttp_debugger``
