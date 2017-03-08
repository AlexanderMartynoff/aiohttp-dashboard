<template>
    <b-navbar toggleable>
        <b-nav-toggle target="nav_collapse"/>
        <router-link to="/"><span>Главная</span></router-link>

        <b-collapse is-nav id="nav_collapse">
            <b-nav is-nav-bar>
                <b-nav-item><router-link to="/docs">Документация</router-link></b-nav-item>
                <b-nav-item><router-link to="/help">Справка</router-link></b-nav-item>
            </b-nav>
        </b-collapse>
    </b-navbar>
</template>

<script type="text/javascript">
    export default {}
</script>