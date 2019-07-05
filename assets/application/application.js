import Vue from 'vue'
import BootstrapVue from 'bootstrap-vue'
import VueRouter from 'vue-router'

import environment from '@/environment';
import {WebSocketService} from '@/websocket'
import {router} from '@/router'

import Box from '@/component/box/box'
import BoxHeader from '@/component/box/box-header'
import BoxBody from '@/component/box/box-body'
import BoxFooter from '@/component/box/box-footer'

import TopMenu from '@/component/menu/top'
import SettingsWindow from '@/component/settings/window'
import IndexGrid from '@/component/requests/master'
import Clock from '@/component/clock/clock'
import DropdpownPane from '@/component/widget/dropdpown-pane'
import Alert from '@/component/widget/alert'
import Layout from '@/component/layout/layout'
import Bar from '@/component/bar/bar'
import Traceback from '@/component/traceback/traceback'
import DatepickerInput from '@/component/datepicker/datepicker-input'


import Axios from '@/axios'


import "@/style/aiohttp-debugger.styl"
import "@/style/bootstrap-override.styl"
import "@/style/datepicker.styl"


Vue.use(Axios)
Vue.use(VueRouter)
Vue.use(BootstrapVue)

const components = {
    Box,
    BoxHeader,
    BoxBody,
    BoxFooter,
    TopMenu,
    IndexGrid,
    Clock,
    DropdpownPane,
    Alert,
    Layout,
    SettingsWindow,
    Bar,
    Traceback,
    DatepickerInput,
}

for (const key in components) {
    Vue.component(key, components[key])
}

const application = new Vue({
    router, el: '.application',
    axios: {
        baseURL: environment.getParameter('aiohttp-dashboard-prefix'),
        interceptor: {
            response(response) {
                return response.data
            }
        }
    }
})
