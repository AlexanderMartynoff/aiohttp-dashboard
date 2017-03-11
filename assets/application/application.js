import Vue from 'vue';
import BootstrapVue from 'bootstrap-vue';
import VueRouter from 'vue-router'

import topMenu from '@/component/menu/top';
import indexGrid from '@/component/index/grid';
import clock from '@/component/clock/clock';
import dropdpownPane from '@/component/widget/dropdpown-pane';
import layout from '@/component/layout/layout';

import {router} from '@/route';

Vue.use(VueRouter);
// register boostrap as global components 
Vue.use(BootstrapVue);

const components = {
    topMenu,
    indexGrid,
    clock,
    dropdpownPane,
    layout
}

for (const key in components) Vue.component(key, components[key]);

const application = new Vue({router, el: "#mount"});