<template>
    <b-modal :hide-header="false"
             :hide-footer="true"
             :centered="true"
             :title="title"
             size="md"
             ref="modal">
        <datepicker-calendar v-model="date"></datepicker-calendar>
    </b-modal>
</template>

<script type="text/javascript">
    import _ from 'lodash'
    import datefns from 'date-fns'

    export default {
        props: {
            name: String,
            format: {
                type: String,
                default: 'dddd, Do MMMM, YYYY',
            },
        },

        data() {
            return {
                date: new Date(),
            }
        },

        computed: {
            eventInputClick() {
                return `datepicker-modal-input:click:${this.name}`
            },

            eventDateChange() {
                return `datepicker-modal-input:change:${this.name}`
            },

            title() {
                if (this.date) {
                    return datefns.format(this.date, this.format)
                }
            },
        },

        watch: {
            date(value) {
                this.$root.$emit(this.eventDateChange, value)
                this.hide()
            }
        },

        methods: {
            show() {
                this.$refs.modal.show()
            },

            hide() {
                this.$refs.modal.hide()
            },
        },

        mounted() {
            this.$root.$on(this.eventInputClick, date => {
                this.date = date
                this.show()
            })
        },
        destroyed() {
            this.$root.$off(this.eventInputClick) 
        }
    }
</script>
