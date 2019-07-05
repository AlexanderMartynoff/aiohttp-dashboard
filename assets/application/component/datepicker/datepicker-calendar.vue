<template>
    <div class="datepicker-calendar" @wheel.stop.prevent="onCalendarMousewheel">
        <table class="datepicker-calendar-table ml-auto mr-auto">
            <thead>
                <th v-for="week in weeks">{{week}}</th>
            </thead>
            <tr v-for="week in calendar">
                <td v-for="date in week">
                    <button type="button"
                            :class="getCalendarBtnSpecialClasses(date)"
                            @click="onDayClick(date)">
                        {{format(date, 'DD')}}
                    </button>
                </td>
            </tr>
        </table>

        <button type="button" @click="onTodayClick" class="mt-1 btn btn-light btn-block border">
            Today
        </button>

        <div class="btn-group btn-block mt-1" role="group">
            <button type="button"
                    class="btn btn-light border-top border-left border-bottom"
                    @click='onShiftClick(-1)'>

                <i class="fas fa-chevron-left"></i>
            </button>
            <button type="button"
                    class="btn btn-block btn-light border-top border-bottom datepicker-calendar-display-month-btn"
                    @click="onShiftModeClick">
                {{displayMode}}
            </button>
            <button type="button" class="btn btn-light border-top border-right border-bottom" @click='onShiftClick(1)'>
                <i class="fas fa-chevron-right"></i>
            </button>
        </div>

    </div>
</template>

<script type="text/javascript">
    import _ from 'lodash'
    import datefns from 'date-fns'

    const modes = {
        month: 'month',
        year: 'year',
    }

    export default {
        props: {
            value: {
                type: [Date, Number]
            }
        },

        data() {
            return {
                mode: modes.month,
                months: {
                    0: 'January',
                    1: 'February',
                    2: 'March',
                    3: 'April',
                    4: 'May',
                    5: 'June',
                    6: 'July',
                    7: 'August',
                    8: 'September',
                    9: 'October',
                    10: 'November',
                    11: 'December',
                },

                weeks: {
                    0: 'Mo',
                    1: 'Tu',
                    2: 'We',
                    3: 'Th',
                    4: 'Fr',
                    5: 'Sa',
                    6: 'Su',
                },

                displayDate: null,
            }
        },

        methods: {
            onCalendarMousewheel(event) {
                if (event.deltaY > 0) {
                    this.onShiftClick(-1)
                } else {
                    this.onShiftClick(1)
                }
            },

            format(date, format) {
                return datefns.format(date, format) 
            },

            isDisplayMonth(date) {
                return datefns.isSameMonth(date, this.displayDate) 
            },

            getCalendarBtnSpecialClasses(date) {
                let classes = ['border', 'btn', 'btn-block']

                if (!datefns.isSameMonth(date, this.displayDate)) {
                    classes.push('disabled')
                }

                if (datefns.isSameDay(date, this.value)) {
                    classes.push('border-primary')
                    classes.push('btn-primary')
                } else {
                    classes.push('btn-light')
                }

                if (datefns.isToday(date)) {
                    classes.push('border-primary')
                }

                return _.uniqBy(classes)
            },

            onDayClick(date) {
                if (datefns.isSameMonth(date, this.displayDate) && !datefns.isSameDay(date, this.value)) {
                    this.$emit('input', date)
                }
            },

            onShiftClick(shift) {
                if (this.isMonthMode()) {
                    this.displayDate = datefns.addMonths(this.displayDate, shift)
                } else if (this.isYearMode()) {
                    this.displayDate = datefns.addYears(this.displayDate, shift)
                }
            },

            onShiftModeClick() {
                if (this.isMonthMode()) {
                    this.mode = modes.year
                } else if (this.isYearMode()) {
                    this.mode = modes.month
                }
            },

            isMonthMode() {
                return _.isEqual(this.mode, modes.month)
            },

            isYearMode() {
                return _.isEqual(this.mode, modes.year)
            },

            onYearClick(shift) {
                this.displayDate = datefns.addYears(this.displayDate, shift)
            },

            onTodayClick() {
                this.$emit('input', new Date())
            },

            getCalendarByDate(date) {
                const startDayCalendar = datefns.startOfWeek(datefns.startOfMonth(date), {weekStartsOn: 1})

                return _.chain()
                    .range(6)
                    .map(weekDayNumber => {
                        const startWeekDay = datefns.addDays(startDayCalendar, weekDayNumber * 7)
                        return datefns.eachDay(startWeekDay, datefns.addDays(startWeekDay, 6))
                    }).value()
            },
        },

        computed: {

            calendar() {
                return this.getCalendarByDate(this.displayDate)
            },

            displayYear() {
                return datefns.getYear(this.displayDate)
            },

            displayMonth() {
                return this.months[datefns.getMonth(this.displayDate)]
            },

            displayMode() {
                if (this.isMonthMode()) {
                    return `${this.displayMonth}/${this.displayYear}`
                } else if (this.isYearMode()) {
                    return `${this.displayYear}/${this.displayMonth}`
                }
            }
        },

        watch: {
            value: {
                immediate: true,
                handler(value) {
                    if (datefns.isDate(this.value)) {
                        this.displayDate = this.value
                    } else {
                        this.displayDate = new Date()
                    }
                }
            },
        },
    }
</script>

