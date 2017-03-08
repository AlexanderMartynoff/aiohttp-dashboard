import VueRouter from 'vue-router';

import IndexGrid from '@/component/index/grid';
import NotFound from '@/component/special/404';

const router = new VueRouter({
    routes: [
        {path: "/", component: IndexGrid},
        {path: "*", component: NotFound}
    ]
});

export {router}
