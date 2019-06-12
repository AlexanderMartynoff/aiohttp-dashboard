<template>
    <b-navbar toggleable type="light" variant="light" class="shadow-sm z-index-1">
        <div class="navbar-controll">
            <b-button variant="light" v-b-toggle.collapse>
                <i class="fas fa-bars"></i>
            </b-button>
        </div>
        <b-navbar-brand class="d-none d-lg-block">
            <code><i class="fas fa-tachometer-alt"></i> [aiottp_dashboard]</code>
        </b-navbar-brand>
        <b-collapse id="collapse" is-nav>
            <b-navbar-nav>
                <b-nav-item href="#/statistic">
                    <code>[DASHBOARD]</code>
                </b-nav-item>
                <b-nav-item href="#/requests">
                    <code>[REQUESTS]</code>
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