<template>
    <ul class="nav">
        <li class="nav-item">
            <dropdpown-pane>
                <a slot="trigger" class="nav-link dropdown-toggle" href="javascript: void(null)">
                    <i class="fa fa-bars" aria-hidden="true"></i>
                </a>
                <div slot="content">
                    <b-card title="<code>[aiohttp_dashboard]</code>" class="aiohttp_dashbord_menu_dropdown">
                        <b-list-group>
                            <router-link to="/" class="list-group-item list-group-item-action">Requests</router-link>
                            <router-link to="/inspect" class="list-group-item list-group-item-action">Inspect</router-link>
                        </b-list-group>
                    </b-card>
                </div>
            </dropdpown-pane>
        </li>
        <li class="nav-item">
            <a class="nav-link" @click="showAboutInfo" href="javascript: void(null)">
                <i class="fa fa-cogs" aria-hidden="true"></i>
            </a>
            <settings-window ref="settingsWindow"></settings-window>
        </li>
    </ul>
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


<style lang="stylus" scoped>
    .card.aiohttp_dashbord_menu_dropdown {
        min-width 350px !important
    }
</style>
