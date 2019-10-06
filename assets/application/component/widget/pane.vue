<template>
    <b-card :class="classes"
            :header="title"
            :bg-variant="activeBgVariant"
            :border-variant="activeBorderVariant"
            :text-variant="activeTextVariant"
            @mouseover="onPaneMouseover"
            @mouseleave="onPaneMouseleave"
            @click="onClick">
       <slot></slot>
    </b-card>
</template>

<script>

export default {
    props: {
        title: {
            type: String,
        },
        variant: {
            type: String,
            default: 'default',
        },
        hoverVariant: {
            type: String,
            default: 'default',
        },
    },
    data () {
        const theme = this.computeTheme(this.variant)

        return {
            activeTextVariant: theme.textVariant,
            activeBgVariant: theme.bgVariant,
            activeBorderVariant: theme.borderVariant,
        }
    },

    computed: {
        classes() {
            let classes = ['pane', 'shadow', 'h-100']

            if (!_.isEqual(this.hoverVariant, this.variant)) {
                classes.push('pointer')
            }
            
            return classes
        }
    },

    methods: {
        onPaneMouseover() {
            this.applyTheme(this.hoverVariant)
        },

        onPaneMouseleave() {
            this.applyTheme(this.variant)
        },

        applyTheme(variant) {
            const theme = this.computeTheme(variant)

            this.activeTextVariant = theme.textVariant
            this.activeBgVariant = theme.bgVariant
            this.activeBorderVariant = theme.borderVariant
        },

        computeTheme(variant) {
            switch (variant) {
                case 'default':
                    return {
                        textVariant: 'default',
                        bgVariant: 'default',
                    }
                case 'dark':
                    return {
                        textVariant: 'white',
                        bgVariant: 'dark',
                    }
                case 'warning':
                    return {
                        textVariant: 'black',
                        bgVariant: 'warning',
                        borderVariant: 'warning',
                    }
                case 'danger':
                    return {
                        textVariant: 'white',
                        bgVariant: 'danger',
                    }
                case 'primary':
                    return {
                        textVariant: 'white',
                        bgVariant: 'primary',
                    }
                case 'success':
                    return {
                        textVariant: 'white',
                        bgVariant: 'success',
                    }
                case 'secondary':
                    return {
                        textVariant: 'white',
                        bgVariant: 'secondary',
                    }
            }
            
        },

        onClick(event) {
            this.$emit('click', event)
        },
    }
}
</script>
