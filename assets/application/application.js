import Vue from 'vue';
import BootstrapVue from 'bootstrap-vue';
import VueRouter from 'vue-router';

import topMenu from '@/component/menu/top';
import indexGrid from '@/component/requests/grid';
import clock from '@/component/clock/clock';
import dropdpownPane from '@/component/widget/dropdpown-pane';
import layout from '@/component/layout/layout';

import {WebSocketService} from '@/websocket';
import {router} from '@/route';

Vue.use(VueRouter);
// register boostrap as global components
Vue.use(BootstrapVue);

WebSocketService.instance = new WebSocketService("ws://127.0.0.1:8080/_debugger/ws/api");

const components = {
    topMenu,
    indexGrid,
    clock,
    dropdpownPane,
    layout
}

for (const key in components) Vue.component(key, components[key]);
const application = new Vue({router, el: "#mount"});