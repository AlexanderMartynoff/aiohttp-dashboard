import Vue from 'vue';
import BootstrapVue from 'bootstrap-vue';
import VueRouter from 'vue-router';

import {WebSocketService} from '@/websocket';
import {router} from '@/router';
import {port} from '@/utils';


import topMenu from '@/component/menu/top';
import indexGrid from '@/component/requests/grid';
import clock from '@/component/clock/clock';
import dropdpownPane from '@/component/widget/dropdpown-pane';
import alert from '@/component/widget/alert';
import layout from '@/component/layout/layout';


Vue.use(VueRouter);
// register boostrap as global components
Vue.use(BootstrapVue);

WebSocketService.instance = new WebSocketService(`ws://${window.location.hostname}:${port}/_debugger/ws/api`);

const components = {
    topMenu,
    indexGrid,
    clock,
    dropdpownPane,
    alert,
    layout
}

for (const key in components) Vue.component(key, components[key]);
const application = new Vue({
    router, el: ".enterpoint"
});