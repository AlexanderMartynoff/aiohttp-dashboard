from aiohttp.web import run_app as run_aiohttp_app
import aiohttp_debugger


if __name__ == '__main__':
    run_aiohttp_app(aiohttp_debugger.application, host='0.0.0.0', port=8080)
