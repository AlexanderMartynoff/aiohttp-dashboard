import VueRouter from 'vue-router';

import IndexGrid from '@/component/requests/master';
import RequestDetail from '@/component/requests/detail';
import RequestMessages from '@/component/messages/master';
import NotFound from '@/component/special/404';
import Statistic from '@/component/statistic/statistic';


export const router = new VueRouter({
    routes: [
        {path: "/", component: Statistic},
        {path: "/statistic", component: Statistic},
        {path: "/requests", component: IndexGrid},
        {path: "/request/detail/:id", component: RequestDetail, props: true},
        {path: "/request/messages/:id", component: RequestMessages, props: true},
        {path: "/messages", component: RequestMessages, props: true},
        {path: "*", component: NotFound}
    ]
});
