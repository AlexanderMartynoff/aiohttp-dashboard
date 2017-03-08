import Vue from 'vue';
import BootstrapVue from 'bootstrap-vue';
import VueRouter from 'vue-router'

import Layout from '@/component/layout/layout';
import {router} from '@/route'

Vue.use(VueRouter);
// register boostrap as global components 
Vue.use(BootstrapVue);

const application = new Vue({
    router,
    components: {"layout": Layout}
}).$mount("#mount");




