<template>
    <b-navbar toggleable type="light" variant="light" class="shadow-sm z-index-1">
        <b-navbar-toggle target="collapse"></b-navbar-toggle>
        <b-navbar-brand>
            <code><i class="fas fa-tachometer-alt"></i> [aiohttp_dashboard]</code>
        </b-navbar-brand>
        <b-collapse id="collapse" is-nav>
            <b-navbar-nav>
                <b-nav-item href="#/" active>
                    <code>[REQUESTS]</code>
                </b-nav-item>
                <b-nav-item href="#/inspect">
                    <code>[ROUTES]</code>
                </b-nav-item>
            </b-navbar-nav>
        </b-collapse>
    </b-navbar>
</template>


<script type="text/javascript">
export default {
    methods: {
        showAboutInfo: function() {
            this.$refs.settingsWindow.show();
        }
    }
}
</script>