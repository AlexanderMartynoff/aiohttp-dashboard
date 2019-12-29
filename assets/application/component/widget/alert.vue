<template>
    <div class="aiohttp-debugger-alert">
        <div class="aiohttp-debugger-content-block">
            <b-alert :show="true" state="warning">
                <i class="fa fa-hourglass" aria-hidden="true"></i> <span class="aiohttp-debugger-aler-block">{{message}}</span>
            </b-alert>
        </div>
    </div>
</template>


<script type="text/javascript">
    export default {
        props: {message: String}
    }
</script>
