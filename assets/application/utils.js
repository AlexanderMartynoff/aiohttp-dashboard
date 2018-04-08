import Vue from 'vue';

const ps = new Vue({});
const port = getPort();


function getPort() {
    return window.location.port ? window.location.port : window.location.protocol == "http:" ? 80 : 443
}

export {port, ps}
