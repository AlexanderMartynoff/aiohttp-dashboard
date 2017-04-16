<template>
    <div class="container-fluid">
        <div class="row">
            <div class="col">
                <ul class="nav">
                    <li class="nav-item">
                        <dropdpown-pane>
                            <a slot="trigger" class="nav-link dropdown-toggle" href="javascript: void(null)">
                                <i class="fa fa-bars" aria-hidden="true"></i>
                            </a>
                            <div slot="content">
                                <div class="card" style="width: 20rem;">
                                    <div class="card-block">
                                        <h4 class="card-title">AiohttpDebbuger</h4>
                                        <div class="list-group">
                                            <router-link to="/" class="list-group-item list-group-item-action">Requests</router-link>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </dropdpown-pane>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" @click="showAboutInfo" href="javascript: void(null)">
                            <i class="fa fa-info-circle" aria-hidden="true"></i>
                        </a>
                        <about-window ref="aboutWindow"></about-window>
                    </li>
                </ul>
            </div>
        </div>
    </div>
</template>


<script type="text/javascript">
export default {
    methods: {
        showAboutInfo: function() {
            this.$refs.aboutWindow.show();
        }
    }
}
</script>


<style lang="stylus" scoped>
    .dropdown
        display inline-flex !important
</style>