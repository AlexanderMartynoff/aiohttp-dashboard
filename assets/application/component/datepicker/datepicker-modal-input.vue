<template>
    <b-form-input :value="displayValue"
                  @input="onInput"
                  @click="onClick"
                  :class="inputClasses"
                  type="text"
                  readonly></b-form-input>
</template>

<script type="text/javascript">
    import _ from 'lodash'
    import * as datefns from 'date-fns'

    export default {
        props: {
            value: {
                type: [Date]
            },
            format: {
                type: String,
                default: 'yyyy/MM/dd H:mm:ss',
            },
            inputClass: {type: String},
            datepickerModal: {type: String},
        },

        data() {
            return {
                displayValue: null,
                displayDate: null,
            }
        },

        computed: {
            inputClasses() {
                return _.chain(this.inputClass).split(' ').concat([
                    'form-control',
                    'datepicker-input',
                ]).value()
            },

            eventInputClick() {
                return `datepicker-modal-input:click:${this.datepickerModal}`
            },

            eventDateChange() {
                return `datepicker-modal-input:change:${this.datepickerModal}`
            },
        },

        watch: {
            value: {
                immediate: true,
                handler(value) {
                    this.displayValue = datefns.format(value, this.format) 
                }
            },
        },

        methods: {
            onInput(value) {
                this.$emit('input', value)
            },

            onClick() {
                this.$root.$emit(this.eventInputClick, this.value)
            },
        },
        
        mounted() {
            this.$root.$on(this.eventDateChange, value => {
                this.onInput(value)
            })
        },

        destroyed() {
            this.$root.$off(this.eventDateChange) 
        }
    }
</script>
