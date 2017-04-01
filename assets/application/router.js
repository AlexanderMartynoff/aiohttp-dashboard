import VueRouter from 'vue-router';

import IndexGrid from '@/component/requests/grid';
import RequestDetail from '@/component/requests/detail';
import NotFound from '@/component/special/404';


const router = new VueRouter({
    routes: [
        {path: "/", component: IndexGrid},
        {path: "/request/detail/:id", component: RequestDetail, props: true},
        {path: "*", component: NotFound}
    ]
});

export {router};
