<template>
    <div class="container-fluid">
        <div class="row">
            <div class="col">
                <ul class="nav">
                    <li class="nav-item">
                        <router-link class="nav-link active" to="/">Главная</router-link>
                    </li>
                    <li class="nav-item">
                        <router-link class="nav-link dropdown-toggle" to="/docs">Меню</router-link>
                    </li>
                    <li class="nav-item">
                        <router-link class="nav-link" to="/help">Справка</router-link>
                    </li>
                    <li class="nav-item">
                        <dropdpown-area>
                            <a slot="trigger" class="nav-link dropdown-toggle">Менюшка</a>
                            <div slot="content">
                                <div class="card" style="width: 20rem;">
                                  <div class="card-block">
                                    <h4 class="card-title">Card title</h4>
                                    <p class="card-text">Some quick example text to build on the card title and make up the bulk of the card's content.</p>
                                    <a href="#" class="btn btn-primary">Go somewhere</a>
                                  </div>
                                </div>
                            </div>
                        </dropdpown-area>
                    </li>
                </ul>
            </div>
        </div>
    </div>
</template>


<script type="text/javascript">
    export default {}
</script>


<style type="text/css" scoped>
    .dropdown {
        display: inline-flex !important;
    }
</style>