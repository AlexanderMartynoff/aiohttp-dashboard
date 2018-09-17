<template>
    <div class="box">
        <slot></slot>
    </div>
</template>


<script type="text/javascript">
    export default {}
</script>


<style lang="stylus">

// MIXINS
box-like()
    flex 1 1 auto

box-direction-column()
    flex-direction column

box-direction-row()
    flex-direction row
    
box()
    box-like()
    display flex
    align-items stretch
    align-content stretch

box-item()
    box-like()
    height 0
    overflow auto

box-scrollable()
    box()
    box-item()

// BOX STYLEs
.box
    box()

.box-body
    box-scrollable()

.box-direction-column
    box-direction-column()
    
.box-direction-row
    box-direction-row()
    
// CARD STYLE
.box.card .card-body
    // overflow auto
    padding 5px
    box-scrollable()
    box-direction-column()

.box.card .tabs
    box()
    box-direction-column()

    .tab-content
        // box-scrollable()
        box()
        box-direction-column()

.card-deck
    box-item()

.container-fluid
    // box()


// HTML STYLE
html, body
    position absolute
    width 100%
    height 100%

body
    box()
    padding-bottom 15px
</style>
