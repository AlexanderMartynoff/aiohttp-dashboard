Dashboard panel for ``aiohttp`` applications
============================================


Features
********

- Fully reactive interface
- Viewing HTTP activity 
- Viewing WebSocket activity 

Install
*******

.. code-block:: shell
        
    pip install aiohttp_debugger

Integrate with application
**************************

.. code-block:: python
        
    import aiohttp_debugger

    application = ...
    
    aiohttp_debugger.setup('/dasboard_home_page', application)


The panel is available at ``<root_url>/dasboard_home_page``
