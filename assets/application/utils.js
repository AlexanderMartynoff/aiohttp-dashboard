import Vue from 'vue'
import {DateTime} from "luxon"

const port = getPort();


const ports = {
    'http:': 80,
    'https:': 443
}

function getPort() {
    return window.location.port ? window.location.port : ports[window.location.protocol]
}


export {port}
