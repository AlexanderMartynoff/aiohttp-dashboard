<template>
    <div class="datepicker input-group" ref="datepickerEl">
        <input ref="datepickerInputEl"
               type="text"
               :class="inputClasses"
               v-model="displayDate"
               @change="onDisplayDateChange"
               @focus="showDatepickerDropdownEl"
               @click.stop/>

            <div class="card datepicker-dropdown"
                 ref="datepickerDropdownEl"
                 v-show="datepickerDropdownElVisible"
                 @click.stop>
                <div class="card-header p-2">
                    {{calendarTitle}}
                </div>
                <div class="card-body p-2">
                    <datepicker-calendar v-model="localValue"></datepicker-calendar>
                </div>
            </div>

        <div class="input-group-append">
            <button class="btn btn-outline-secondary" type="button" @click.stop="doFocus()">
                <i class="far fa-calendar-alt"></i>
            </button>
        </div>
    </div>
</template>

<script type="text/javascript">
    import _ from 'lodash'
    import Popper from 'popper.js'
    import datefns from 'date-fns'

    import DatepickerCalendar from './datepicker-calendar'


    export default {
        components: {
            'datepicker-calendar': DatepickerCalendar,
        },
        props: {
            value: {
                type: [Date, Number]
            },
            mode: {
                type: String,
                default: 'timestamp'
            },
            format: {
                type: String,
                default: 'YYYY/MM/DD',
            },
            inputClass: {type: String},
        },
        data() {
            return {
                localValue: null,
                displayDate: null,
                datepickerDropdownElVisible: false,
            }
        },
        computed: {
            inputClasses() {
                return _.chain(this.inputClass).split(' ').concat('form-control').value()
            },

            calendarTitle() {
                return datefns.format(this.value || new Date(), 'dddd, Do MMMM, YYYY')
            },
        },
        methods: {
            initPopper() {
                this.$popper = new Popper(this.$refs.datepickerEl, this.$refs.datepickerDropdownEl, {
                    placement: 'bottom-start',
                    modifiers: {
                        offset: {
                            enabled: true,
                            offset: '0, 5',
                        },
                    }
                })
            },

            doFocus() {
                this.$refs.datepickerInputEl.focus()
            },

            hideDatepickerDropdownEl() {
                this.datepickerDropdownElVisible = false
            },

            showDatepickerDropdownEl() {
                this.datepickerDropdownElVisible = true

                this.$nextTick(() => {
                    this.$popper.update()                    
                })
            },

            attacheEventToDocument() {
                document.addEventListener('click', this.bodyClickEventListener = () => this.hideDatepickerDropdownEl())
            },
            
            removeEventToDocument() {
                document.removeEventListener('click', this.bodyClickEventListener)
            },

            onDisplayDateChange() {
                const displayDate = datefns.parse(this.displayDate, this.format)

                if (datefns.isDate(displayDate) && datefns.isValid(displayDate)) {
                    this.$emit('input', displayDate)
                } else {
                    this.$emit('input', null)
                }
            },

            onCalendarDateChange(value) {
                this.$emit('input', value)
            },
        },

        watch: {
            value: {
                immediate: true,
                handler(value) {
                    this.localValue = value
                    this.displayDate = datefns.isDate(value) ? datefns.format(value, this.format) : null

                    this.hideDatepickerDropdownEl()
                }
            },

            localValue(value) {
                this.$emit('input', value)
            }
        },

        mounted() {
            this.initPopper()
            this.attacheEventToDocument()
        },

        destroyed() {
            this.removeEventToDocument()
        }
    }
</script>
