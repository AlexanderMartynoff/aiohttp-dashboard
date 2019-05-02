<template>
    <div class="container-fluid my-3">

        <bar v-if="messages" sticky="top">
            <b-nav>
                <b-nav-item active @click="openMessages">
                    <i class="fas fa-arrows-alt-v"></i> {{wsTotal}}
                    <i class="fa fa-long-arrow-alt-down"></i> {{wsIncomingTotal}}
                    <i class="fa fa-long-arrow-alt-up" aria-hidden="true"></i> {{wsOutboundTotal}}
                </b-nav-item>
            </b-nav>
        </bar>

        <div class="row mt-3">
            <div class="col-md-6">
                <b-card class="shadow h-100" title="Info">
                    <ul class="list-group overflow-auto" v-if="record">
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
                            <span>Begin time:</span> <code>{{record.begintime}}</code>
                        </li>
                        <li class="list-group-item">
                            <span>Done time:</span> <code>{{record.donetime}}</code>
                        </li>
                        <li class="list-group-item">
                            <span>Scheme:</span> <code>{{record.scheme}}</code>
                        </li>
                    </ul>
                    <alert v-else message="Records not found"></alert>
                </b-card>
            </div>
            <div class="col-md-6 mt-3 mt-md-0">
                <b-card no-block no-body class="shadow h-100">
                    <b-tabs small pills card no-fade>
                        <b-tab title="Request headers">
                            <b-list-group v-if="record">
                                <b-list-group-item button v-for="value, key in record.reqheaders">
                                    <span>{{key}}:</span> <code>{{truncate(value)}}</code>
                                </b-list-group-item>
                            </b-list-group>

                            <alert v-else message="Records not found"></alert>
                        </b-tab>
                        <b-tab title="Response headers">
                            <ul class="list-group" v-if="record">
                                <li class="list-group-item" v-for="(value, key) in record.resheaders">
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
            <div class="col-md">
                <traceback :exception="exception"></traceback>
            </div>
        </div>
    </div>
</template>


<script>
    import {router} from '@/router';
    import {WebSocketService} from '@/websocket'

    export default {
        mixins: [WebSocketService.mixin],
        data: function() {
            return {
                record: {},
                wsCurrentPage: 1,
                wsPerPage: 25,
                wsTotal: 0,
                messages: null,
                exception: null,
                showWsLastPageSetting: false,
                wsIncomingTotal: 0,
                wsOutboundTotal: 0,
            }
        },
        props: {
            id: String
        },

        methods: {
            openMessages() {
                router.push({path: `/request/messages/${this.id}`})
            },

            onRequestRecive: function(data) {
                this.record = data.item;
            },

            onWsMessagesRecive: function(data) {
                this.messages = data.collection
                this.wsTotal = data.total
                this.wsIncomingTotal = data.incoming
                this.wsOutboundTotal = data.outbound
            },

            onExceptionRecive(data) {
                this.exception = data.item
            },

            showWsDetail: function(record) {
                this.wsRecord = record
                this.$refs.wsDetail.show()
            },

            onDetailShown: function() {
                this.wsUnsubscribe()
            },

            onDetailHidden: function() {
                this.wsSubscribe()
            },

            truncate(string, limit=50) {
                if (string && string.length > limit) {
                    return string.substr(0, limit) + ' ...'
                }

                return string
            },

            requestSubscribe: function() {
                return this.httpSubscription = this.subscribe('request', message => {
                    this.onRequestRecive(message.data)
                }, {
                    'id': parseInt(this.id)
                })
            },

            wsSubscribe: function() {
                this.wsSubscription = this.subscribe('request.messages', message => {
                    this.onWsMessagesRecive(message.data)
                }, {
                    'id': parseInt(this.id),
                    'limit': this.wsPerPage,
                    'page': this.wsCurrentPage
                })
            },

            exceptionSubscribe() {
                this.errorSubscribtion = this.subscribe('request.exception', message => {
                    this.onExceptionRecive(message.data)
                }, {
                    'id': parseInt(this.id)
                })
            },

            errorUnsubscribe: function(onComplete) {
                this.unsibscribe(this.errorSubscribtion, onComplete)
            },

            wsUnsubscribe: function(onComplete) {
                this.unsibscribe(this.wsSubscription, onComplete)
            },

            httpUnsubscribe: function(onComplete) {
                this.unsibscribe(this.httpSubscription, onComplete)
            }
        },

        created: function() {
            this.wsSubscribe()
            this.requestSubscribe()
            this.exceptionSubscribe()
        },
        
        destroyed: function() {
            this.wsUnsubscribe()
            this.httpUnsubscribe()
            this.errorUnsubscribe()
        }
    }
</script>

