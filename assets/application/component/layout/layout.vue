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


<style lang="stylus">
    html, body
        min-height 100%
        position absolute
        width 100%
        
    table .sorting
        cursor pointer
        
    table tr td
        font-size: 12px
        
    .pointer
        cursor: pointer
</style>