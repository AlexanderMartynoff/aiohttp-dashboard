<template>
    <div class="row" :class="containerClasses">
        <div class="col-12">
            <b-card no-body :class="cardClasses" bg-variant="light" v-if="card">
                <slot></slot>
            </b-card>
            <slot v-else></slot>
        </div>
    </div>
</template>


<script type="text/javascript">
    export default {
        props: {
            sticky: String,
            card: {
                type: Boolean,
                default: true,
            },
            align: {
                type: String,
                default: 'left'
            },
            offset: {
                type: String,
                default: '1',
            }
        },

        computed: {
            containerClasses() {
                var clases = []

                if (this.sticky === 'top') {
                    clases.push('sticky-top')
                    clases.push('sticky-top-' + this.offset)
                } else if (this.sticky === 'bottom') {
                    clases.push('sticky-bottom')
                    clases.push('sticky-bottom-' + this.offset)
                }

                return clases
            },

            cardClasses() {
                return ['shadow-sm']
            }
        }
    }
</script>

