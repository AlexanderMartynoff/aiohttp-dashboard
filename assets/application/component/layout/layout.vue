<template>
    <div>
        <top-menu></top-menu>
        <router-view></router-view>
    </div>
</template>


<script>
import TopMenu from '@/component/menu/top';
import IndexGrid from '@/component/index/grid';


export default {
    components: {
        'top-menu': TopMenu,
        'index-grid': IndexGrid
    },
    data: () => ({
        dropdownSelectList: [
            {text: "Один"},
            {text: "Два"},
            {text: "Три"}
        ]
    })
}
</script>


<style>
    .sorting {
        cursor: pointer;
    }
</style>