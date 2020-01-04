<template type="text/html">
    <div class="container-fluid my-3">

        <datepicker-modal name="datepicker-datestart"></datepicker-modal>
        <datepicker-modal name="datepicker-datestop"></datepicker-modal>

        <div class="row mt-3">
            <div class="col-md-6">
                <pane title="Status">
                    <h2>
                        <code>{{formatDateTime(startupTime)}}</code>
                        <span class="d-block text-small">application start time</span>
                    </h2>
                    <h2>
                        <code>{{startupDuration}}</code>
                        <span class="d-block text-small">application work duration</span>
                    </h2>
                </pane>
            </div>

            <div class="col-md-6 mt-3 mt-md-0">
                <pane title="Settings">
                    <b-form class="mt-3">
                        <b-row>
                            <b-col md="12">
                                <b-input-group>
                                    <div class="input-group-prepend">
                                        <button class="btn btn-primary" type="button">
                                            <i class="far fa-calendar-alt"></i>
                                        </button>
                                    </div>
                                    <datepicker-modal-input name="datestart"
                                                            datepicker-modal="datepicker-datestart"
                                                            v-model="filter.datestart">
                                    </datepicker-modal-input>
                                    <datepicker-modal-input name="datestop"
                                                            datepicker-modal="datepicker-datestop"
                                                            v-model="filter.datestop">
                                    </datepicker-modal-input>
                                </b-input-group>
                                <span class="d-block text-small">what interval are you interested in?</span>
                            </b-col>
                        </b-row>
                    </b-form>
                </pane>
            </div>

        </div>

        <div class="row mt-3 mb-3">
            <div class="col-md-6 mb-3 mb-md-0">

                <pane title="Requests" @click="onRequestClick">
                    
                    <b-row>
                        <b-col md="6">
                            <h2>
                                <code>{{requestsCount}}</code>
                                <span class="d-block text-small">total number</span>
                            </h2>  
                        </b-col>
                        <b-col md="6">
                            <h2>
                                <code>{{requestsPerSecond}}</code>
                                <span class="d-block text-small">number per second</span>
                            </h2>
                        </b-col>
                    </b-row>
                </pane>
            </div>
            <div class="col-md-6">
                <pane title="Messages" @click="onMessagesClick">
                    <b-row>
                        <b-col md="6">
                            <h2>
                                <code>{{messagesCount}}</code>
                                <span class="d-block text-small">total number</span>
                            </h2>
                        </b-col>
                        <b-col md="6">
                            <h2>
                                <code>{{messagesPerSecond}}</code>
                                <span class="d-block text-small">number per second</span>
                            </h2>
                        </b-col>
                    </b-row>
                </pane>
            </div>
        </div>

        <div class="row mt-3">
            <div class="col-md-6">
                <pane title="Exceptions">
                    <h2>
                        <code>{{requestsErrorCount}}</code>
                        <span class="d-block text-small">total number</span>
                    </h2>
                </pane>
            </div>
        </div>
    </div>
</template>


<script type="text/javascript">
    import {EventService} from '@/websocket'
    import {router} from '@/router'
    import {formatDateTime} from "@/misc"
    import {
        startOfDay,
        addDays,
        getTime,
        fromUnixTime,
        format,
        formatDistance,
        formatDistanceStrict,
    } from 'date-fns'


    export default {
        data: () => {
            const datestart = startOfDay(new Date())
            const datestop = addDays(datestart, 1)

            return {
                requestsCount: 0,
                requestsErrorCount: 0,
                messagesIncomingCount: 0,
                messagesOutcomingCount: 0,
                startupTime: new Date(0),
                nowTime: new Date(),
                filter: {
                    datestart: datestart,
                    datestop: datestop,
                },
            }
        },
        
        methods: {
            onRequestClick() {
                router.push({path: `/requests`})
            },
            onMessagesClick() {
                router.push({path: `/messages`})
            },

            formatDateTime(datetime) {
                return format(datetime, 'cccc, yyyy, HH:mm:ss')
            },

            loadRequestsStatus() {
                return this.$axios.get(`/api/status/request`, {
                    params: {
                        datestart: getTime(this.filter.datestart),
                        datestop: getTime(this.filter.datestop),
                    }
                }).then(status => {
                    this.requestsCount = status.count
                }) 
            },

            loadMessagesStatus() {
                return this.$axios.get(`/api/status/message`, {
                    params: {
                        datestart: getTime(this.filter.datestart),
                        datestop: getTime(this.filter.datestop),
                    }
                }).then(status => {
                    this.messagesIncomingCount = status.websocket.countincoming
                    this.messagesOutcomingCount = status.websocket.countoutcoming
                }) 
            },

            loadErrorsStatus() {
                return this.$axios.get(`/api/status/error/request`, {
                    params: {
                        datestart: getTime(this.filter.datestart),
                        datestop: getTime(this.filter.datestop),
                    }
                }).then(status => {
                    this.requestsErrorCount = status.count
                }) 
            },

            loadStatus() {
                return this.$axios.get('/api/status').then(status => {
                    this.startupTime = fromUnixTime(status['timestart'])
                }) 
            },

            startInterval() {
                this.$interval = setInterval(() => {
                    this.nowTime = new Date()
                }, 1000)
            },

            stopInterval() {
                clearInterval(this.$interval)
            },
        },

        computed: {
            startupDuration() {
                return formatDistanceStrict(this.startupTime, this.nowTime)
            },

            requestsPerSecond() {
                return 0
            },

            messagesPerSecond() {
                return 0
            },

            messagesCount() {
                return this.messagesIncomingCount + this.messagesOutcomingCount
            },
        },

        watch: {
            'filter.datestop'(value) {
                this.loadMessagesStatus()
                this.loadRequestsStatus()
                this.loadErrorsStatus()
            },
            'filter.datestart'(value) {
                this.loadMessagesStatus()
                this.loadRequestsStatus()
                this.loadErrorsStatus()
            },
        },

        created() {
            this.$event = EventService.create()

            this.$event.on('websocket', event => {
                this.loadMessagesStatus()
            })

            this.$event.on('http', event => {
                this.loadRequestsStatus()
                this.loadErrorsStatus()
            })

            this.loadStatus()
            this.startInterval()
        },

        destroyed() {
            this.stopInterval()
        },

    }
</script>
