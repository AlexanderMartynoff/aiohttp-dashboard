import Vue from 'vue';
import BootstrapVue from 'bootstrap-vue';
import VueRouter from 'vue-router';

import {WebSocketService} from '@/websocket';
import {router} from '@/router';
import {port} from '@/utils'; 

// component block
import TopMenu from '@/component/menu/top';
import SettingsWindow from '@/component/settings/window';
import IndexGrid from '@/component/requests/grid';
import Clock from '@/component/clock/clock';
import DropdpownPane from '@/component/widget/dropdpown-pane';
import InspectMaster from '@/component/inspect/master';
import Alert from '@/component/widget/alert';
import Layout from '@/component/layout/layout';


Vue.use(VueRouter);
// register boostrap as global components
Vue.use(BootstrapVue);

const components = {
    TopMenu,
    IndexGrid,
    Clock,
    DropdpownPane,
    Alert,
    InspectMaster,
    Layout,
    SettingsWindow
}

for (const key in components) Vue.component(key, components[key]);
const application = new Vue({router, el: ".enterpoint"});