import Vue from 'vue';

const ps = new Vue({});
const port = getPort();


const portsMap = {
    'http:': 80,
    'https:': 443
};

function getPort() {
    return window.location.port ? window.location.port : portsMap[window.location.protocol]
}

export {port, ps}
