<template>
    <div class="aiohttp-debugger__alert">
        <div class="aiohttp-debugger__alert__content-block">
            <b-alert :show="true" state="warning">
                <i class="fa fa-hourglass" aria-hidden="true"></i> <span class="aiohttp-debugger__aler-block">{{message}}</span>
            </b-alert>
        </div>
    </div>
</template>


<script type="text/javascript">
    export default {
        props: {message: String}
    }
</script>


<style lang="stylus">
    .aiohttp-debugger__alert
        width 50%
        margin 0 auto
        
        .aiohttp-debugger__alert__content-block
            margin auto
            
            .aiohttp-debugger__aler-block
                margin 0 0 0 5px
</style>
