<template>
    <div class="container-fluid my-3">

        <bar v-if="wsLength" sticky="top">
            <b-nav>
                <b-nav-item active @click="openMessages">
                    <i class="fas fa-arrows-alt-v"></i> {{wsLength}}
                    <i class="fa fa-long-arrow-alt-down"></i> {{wsIncomingLength}}
                    <i class="fa fa-long-arrow-alt-up" aria-hidden="true"></i> {{wsOutcomingLength}}
                </b-nav-item>
            </b-nav>
        </bar>

        <div class="row mt-3" v-if="record">
            <div class="col-md-6">
                <b-card class="shadow h-100" title="Info">
                    <ul class="list-group overflow-auto">
                        <li class="list-group-item list-group-item-warning block" v-if="record.status || record.reason">
                            <div>
                                <span>{{record.status}}</span>
                            </div>
                            <div>
                                <small class="text-muted">{{record.reason}}</small>
                            </div>
                        </li>
                        <li class="list-group-item">
                            <span>Client IP:</span> <code>{{record.ip}}</code>
                        </li>
                        <li class="list-group-item">
                            <span>Path:</span> <code>{{record.path}}</code>
                        </li>
                        <li class="list-group-item">
                            <span>Begin time:</span> <code>{{record.starttime}}</code>
                        </li>
                        <li class="list-group-item">
                            <span>Done time:</span> <code>{{record.stoptime}}</code>
                        </li>
                        <li class="list-group-item">
                            <span>Scheme:</span> <code>{{record.scheme}}</code>
                        </li>
                    </ul>

                    <b-card class="mt-2">
                        <code v-if="record.body">
                            <pre class="my-0">{{record.body}}</pre>
                        </code>
                        <code v-else>
                            [EMPTY BODY]
                        </code>
                    </b-card>

                </b-card>
            </div>
            <div class="col-md-6 mt-3 mt-md-0">
                <b-card no-block no-body class="shadow h-100">
                    <b-tabs small pills card>
                        <b-tab title="Request">
                            <template slot="title">
                                <i class="fas fa-arrow-right"></i> Headers
                            </template>

                            <b-list-group v-if="record">
                                <b-list-group-item button v-for="value, key in record.requestheaders">
                                    <span>{{key}}:</span> <code>{{truncate(value)}}</code>
                                </b-list-group-item>
                            </b-list-group>

                            <alert v-else message="Records not found"></alert>
                        </b-tab>
                        <b-tab title="Response">

                            <template slot="title">
                                <i class="fas fa-arrow-left"></i> Headers
                            </template>

                            <ul class="list-group" v-if="record">
                                <li class="list-group-item" v-for="(value, key) in record.responseheaders">
                                    <span>{{key}}:</span> <code>{{truncate(value)}}</code>
                                </li>
                            </ul>
                            <alert v-else message="Records not found"></alert>
                        </b-tab>
                    </b-tabs>
                </b-card>
            </div>
        </div>

        <div class="row mt-3" v-if="exception">
            <div class="col-md-12">
                <traceback :exception="exception"></traceback>
            </div>
        </div>
    </div>
</template>


<script>
    import {router} from '@/router';
    import {WebSocketService} from '@/websocket'

    export default {
        data: function() {
            return {
                record: null,
                exception: null,
                wsIncomingLength: 0,
                wsOutcomingLength: 0,
            }
        },
        props: {
            id: String
        },

        computed: {
            wsLength() {
                return this.wsIncomingLength + this.wsOutcomingLength
            }
        },

        methods: {
            openMessages() {
                router.push({path: `/request/messages/${this.id}`})
            },

            truncate(string, limit=50) {
                if (string && string.length > limit) {
                    return string.substr(0, limit) + ' ...'
                }

                return string
            },

            loadRequest() {
                return this.$axios.get(`/dashboard/api/request/${this.id}`).then(request => {
                    this.record = request
                }) 
            },

            subscribeWs: function() {
                this.$event.on('websocket', message => {
                    console.log(message)
                }, {
                    request: this.id,
                })
            },

            subscribeRequest: function() {
                this.$event.on('http', request => {
                    console.log(request)
                }, {
                    request: this.id,
                })
            },
        },

        created: function() {
            this.$event = WebSocketService.create()

            this.loadRequest()
            this.subscribeWs()
            this.subscribeRequest()
        },
        
        destroyed: function() {
            this.$event.off()
        }
    }
</script>

