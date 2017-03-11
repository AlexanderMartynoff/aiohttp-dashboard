<template>
    <div>
        <top-menu></top-menu>
        <div class="container-fluid">
            <div class="row">
                <div class="col">
                    <router-view></router-view>
                </div>
            </div>
        </div>
    </div>
</template>


<script>
export default {}
</script>


<style>
    .sorting {
        cursor: pointer;
    }
</style>