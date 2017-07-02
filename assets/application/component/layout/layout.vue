<template>
    <div class="aiohttp-debugger__layout">
        <top-menu></top-menu>
        <div class="container-fluid aiohttp-debugger__layout__content">
            <div class="row flex-vertical d-flex align-items-stretch">
                <div class="col d-flex align-items-stretch">
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
        position absolute
        width 100%
        display flex
        flex-direction column

    html
        min-height 100%
        
    body
        top 0
        bottom 10px
        
    .aiohttp-debugger__layout
        flex 1
        display flex
        flex-direction column
        
    .flex-column
        display flex
        flex-direction column
    
    .aiohttp-debugger__layout__content
        flex auto
        display flex
        flex-direction column

    .flex-vertical
        flex auto
        
    .container-fluid
        margin-left 0
        margin-right 0
        
    .card.flex-card
        flex auto
        display flex
        flex-direction column
        min-height min-content
        
    .card.flex-card .card-block 
        flex auto
        height 0
        overflow auto
    
    .card.flex-card.grey-card-bg .card-block
        background rgba(247, 247, 249, 0.48)
            
    .card.flex-card .tabs
        flex auto
        flex-direction column
        display flex
        
    .d-flex
        flex auto
        
    .tab-content
        display flex
        .tab-pane
            flex auto
    button
        cursor pointer
        
    .table td
        font-size 14px
        vertical-align middle
        
    .list-group .list-group-item
        padding 6px
        
    .block
        display block
        
    .modal-huge .modal-dialog
        max-width: 60%
        
    pre
        background #f7f7f9
        border-radius 5px
        padding 5px
    pre code
        color #bd4147
</style>