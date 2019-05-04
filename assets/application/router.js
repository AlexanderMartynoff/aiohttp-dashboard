import VueRouter from 'vue-router';

import IndexGrid from '@/component/requests/grid';
import RequestDetail from '@/component/requests/detail';
import RequestMessages from '@/component/requests/messages';
import NotFound from '@/component/special/404';
import InspectMaster from '@/component/inspect/master';
import Statistic from '@/component/statistic/statistic';


export const router = new VueRouter({
    routes: [
        {path: "/", component: Statistic},
        {path: "/statistic", component: Statistic},
        {path: "/requests", component: IndexGrid},
        {path: "/request/detail/:id", component: RequestDetail, props: true},
        {path: "/request/messages/:id", component: RequestMessages, props: true},
        {path: "/inspect", component: InspectMaster},
        {path: "*", component: NotFound}
    ]
});
