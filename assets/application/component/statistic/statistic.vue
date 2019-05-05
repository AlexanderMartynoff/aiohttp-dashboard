<template type="text/html">
    <div class="container-fluid my-3">
        <div class="row mt-3 mb-3">
            
            <div class="col-md-6">
                <b-card class="shadow h-100" title="Time">
                    <h2>
                        <code>{{formatDateTime(startupTime)}}</code>
                        <span class="d-block text-muted text-small">application start time</span>
                    </h2>
                    <h2>
                        <code>{{startupDuration}}</code>
                        <span class="d-block text-muted text-small">application work duration</span>
                    </h2>
                </b-card>
            </div>

            <div class="col-md-6 mt-3 mt-md-0">
                <b-card class="shadow h-100" title="Exceptions">
                    <h2>
                        <code>558 068</code>
                        <span class="d-block text-muted text-small">total number</span>
                    </h2>
                </b-card>
            </div>

        </div>
        <div class="row mt-3 mb-3">
            <div class="col-md-6">
                <b-card class="shadow h-100" title="Requests">
                    <h2>
                        <code>{{requestsCount}}</code>
                        <span class="d-block text-muted text-small">total number</span>
                    </h2>
                    <h2>
                        <code>{{requestsPerSecond}}</code>
                        <span class="d-block text-muted text-small">number per second</span>
                    </h2>
                </b-card>
            </div>
            <div class="col-md-6 mt-3 mt-md-0">
                <b-card class="shadow h-100" title="Messages">
                    <h2>
                        <code>{{messagesCount}}</code>
                        <span class="d-block text-muted text-small">total number</span>
                    </h2>
                    <h2>
                        <code>{{messagesPerSecond}}</code>
                        <span class="d-block text-muted text-small">number per second</span>
                    </h2>
                </b-card>
            </div>
        </div>
    </div>
</template>


<script type="text/javascript">
    import {DateTime} from "luxon"
    import {WebSocketService} from '@/websocket'
    import {formatDateTime} from "@/misc"

    export default {
        mixins: [WebSocketService.mixin],
        data: () => ({
            requestsCount: 0,
            messagesCount: 0,
            startupTime: DateTime.utc(0),
            now: DateTime.utc(),
        }),
        methods: {
            formatDateTime(datetime) {
                return formatDateTime(datetime)
            },

            requestsSubscribe() {
                this.requestsSubscribtion = this.subscribe('request.requests.count', message => {
                    this.requestsCount = message.data
                })
            },

            messagesSubscribe() {
                this.messagesSubscribtion = this.subscribe('request.messages.count', message => {
                    this.messagesCount = message.data
                })
            },

            fetchTime() {
                this.subscribe('fetch.times', message => {
                    this.startupTime = DateTime.fromSeconds(message.data.startup)
                })
            },

            startInterval() {
                this.$interval = setInterval(() => {
                    this.now = DateTime.utc()
                }, 1000)
            },

            stopInterval() {
                clearInterval(this.$interval)
            }
        },

        computed: {
            startupDuration() {
                return this.now.diff(this.startupTime).toFormat('dd:hh:mm:ss')
            },

            requestsPerSecond() {
                return (this.requestsCount / this.now.diff(this.startupTime).as('seconds')).toFixed(2)
            },

            messagesPerSecond() {
                return (this.messagesCount / this.now.diff(this.startupTime).as('seconds')).toFixed(2)
            }
        },

        destroyed() {
            this.stopInterval()
        },

        created() {
            this.fetchTime()
            this.messagesSubscribe()
            this.requestsSubscribe()
            this.startInterval()
        },
    }
</script>
