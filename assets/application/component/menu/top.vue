<template>

<b-navbar toggleable="lg" type="light" variant="light" class="shadow-sm">
    <b-navbar-brand href="#">
        <code><i class="fas fa-tachometer-alt"></i> [aiottp_dashboard]</code>
    </b-navbar-brand>

    <b-navbar-toggle target="collapse"></b-navbar-toggle>

    <b-collapse id="collapse" is-nav>
        <b-navbar-nav>
            <b-nav-item href="#/statistic">
                <i class="fas fa-chart-bar"></i> Overview
            </b-nav-item>
            <b-nav-item href="#/requests">
                <i class="fas fa-globe"></i> HTTP
            </b-nav-item>
            <b-nav-item href="#/messages">
                <i class="fas fa-plug"></i> WebSocket
            </b-nav-item>
            <b-nav-item href="#/sql">
                <i class="fas fa-database"></i> SQL
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