<template>
    <div>
        <span class="dropdown-trigger"
              @click="triggerShow()"
              @mouseover="triggerShow()"
              @mouseout="triggerHide()"
              ref="triggerEl">

            <slot name="trigger"></slot>
        </span>
        <div class="dropdown-layout"
             @mouseover="triggerShow()"
             @mouseout="triggerHide()"
             ref="dropdownEl">
            <slot name="content"></slot>
        </div>
    </div>
</template>


<script>
import Tether from 'tether';


export default {
    data: () => ({
        show: true
    }),
    methods: {
        triggerShow: function() {
            this.$refs.dropdownEl.style.display = 'block';
            const tether = new Tether({
                element: this.$refs.dropdownEl,
                target: this.$refs.triggerEl.children[0],
                attachment: 'top right',
                targetAttachment: 'bottom right'
            });
            tether.position();
        },
        triggerHide: function() {
            this.$refs.dropdownEl.style.display = 'none';
        }
    }
}
</script>


<style type="text/css" scoped>
    .dropdown-layout {
        z-index: 10000;
        display: none;
    }
    .dropdown-trigger {
        cursor: pointer;
    }
</style>