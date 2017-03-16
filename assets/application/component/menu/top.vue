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
                                            <router-link to="/help" class="list-group-item list-group-item-action">Logs</router-link>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </dropdpown-pane>
                    </li>
                </ul>
            </div>
        </div>
    </div>
</template>


<script type="text/javascript">
export default {}
</script>


<style lang="stylus" scoped>
    .dropdown
        display inline-flex !important
</style>