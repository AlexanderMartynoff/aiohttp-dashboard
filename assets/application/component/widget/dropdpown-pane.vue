<template>
    <div>
        <span class="dropdown-trigger" @click.stop="dropdownOnOff()" ref="triggerEl">
            <slot name="trigger"></slot>
        </span>
        <div class="dropdown-layout" ref="dropdownEl">
            <slot name="content"></slot>
        </div>
    </div>
</template>


<script>
import Tether from 'tether';

export default {
    props: {
        attachment: {
            type: String,
            default: "top left"
        },
        targetAttachment: {
            type: String,
            default: "bottom left"
        }
    },
    methods: {
        dropdownIsVisible: function() {
            return this.$refs.dropdownEl.style.display === 'block';
        },
        dropdownOnOff: function() {
            return this.dropdownIsVisible() ? this.dropdownHide() : this.dropdownShow();
        },
        dropdownShow: function() {
            this.dropdownElShow();
            this.tether.position();
        },
        dropdownHide: function() {
            this.dropdownElHide();
        },
        dropdownElShow: function() {
            this.$refs.dropdownEl.style.display = 'block';
        },
        dropdownElHide: function() {
            this.$refs.dropdownEl.style.display = 'none';
        },
        newTether: function() {
            return new Tether({
                element: this.$refs.dropdownEl,
                target: this.$refs.triggerEl.children[0],
                attachment: this.attachment,
                targetAttachment: this.targetAttachment,
                constraints: [
                    {
                        to: 'scrollParent',
                        pin: true
                    },
                    {
                        to: 'window',
                        attachment: 'together'
                    }
                ]
            });
        }
    },
    mounted: function() {
        document.addEventListener('click', this.dropdownHide);
        this.dropdownElHide();
        this.tether = this.newTether();
    }
}
</script>


<style lang="stylus" scoped>
    .dropdown-layout
        z-index 10000
    .dropdown-trigger
        cursor pointer
</style>