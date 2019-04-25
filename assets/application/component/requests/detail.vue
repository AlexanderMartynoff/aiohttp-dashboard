<template>
     <div class="container-fluid my-3">

        <cardnavbar v-if="wsCollection" sticky="top">
            <b-nav-item active @click="messages()">
                <i class="fas fa-arrows-alt-v"></i> {{wsTotal}}
                <i class="fa fa-long-arrow-alt-down"></i> {{wsIncomingTotal}}
                <i class="fa fa-long-arrow-alt-up" aria-hidden="true"></i> {{wsOutboundTotal}}
            </b-nav-item>
        </cardnavbar>

        <div class="row mt-3">
            <div class="col-md-6">
                <b-card class="shadow h-100" title="Request">
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
                            <span class="key-name">Client IP:</span> <code>{{record.ip}}</code>
                        </li>
                        <li class="list-group-item">
                            <span class="key-name">Path:</span> <code>{{record.path}}</code>
                        </li>
                        <li class="list-group-item">
                            <span class="key-name">Begin time:</span> <code>{{record.begintime}}</code>
                        </li>
                        <li class="list-group-item">
                            <span class="key-name">Done time:</span> <code>{{record.donetime}}</code>
                        </li>
                        <li class="list-group-item">
                            <span class="key-name">Scheme:</span> <code>{{record.scheme}}</code>
                        </li>
                    </ul>
                    <alert v-else message="Records not found"></alert>
                </b-card>
            </div>
            <div class="col-md-6 mt-3 mt-md-0">
                <b-card no-block no-body class="shadow h-100 box box-direction-column">
                    <b-tabs small pills card no-fade>
                        <b-tab title="Request headers">
                            <b-list-group v-if="record">
                                <b-list-group-item button v-for="value, key in record.reqheaders">
                                    <span class="key-name">{{key}}:</span> <code>{{truncate(value)}}</code>
                                </b-list-group-item>
                            </b-list-group>

                            <alert v-else message="Records not found"></alert>
                        </b-tab>
                        <b-tab title="Response headers">
                            <ul class="list-group" v-if="record">
                                <li class="list-group-item" v-for="(value, key) in record.resheaders">
                                    <span class="key-name">{{key}}:</span> <code>{{truncate(value)}}</code>
                                </li>
                            </ul>
                            <alert v-else message="Records not found"></alert>
                        </b-tab>
                    </b-tabs>
                </b-card>
            </div>
        </div>
    </div>
</template>


<script>
    import {router} from '@/router';
    import {WebSocketService} from '@/websocket'
    import {ps} from '@/utils'

    export default {
        mixins: [WebSocketService.mixin],
        data: function() {
            return {
                record: {},
                wsRecord: {},
                wsCurrentPage: 1,
                wsPerPage: 25,
                wsTotal: 0,
                wsCollection: [],
                goToNextWsPage: false,
                showWsLastPageSetting: false,
                wsIncomingTotal: 0,
                wsOutboundTotal: 0,
            }
        },
        props: {
            id: String
        },
        computed: {
            isNotWs: function() {
                return !(this.wsCollection || {}).length
            },

            isWsOnLastPage: function() {
                return this.wsCurrentPage == this.lastWsPageNumber
            },

            lastWsPageNumber: function() {
                return Math.ceil(this.wsTotal / this.wsPerPage)
            }
        },
        watch: {
            wsCurrentPage: function(page) {
                this.wsUnsubscribe(() => this.wsSubscribe())
            },

            wsCollection: function() {
                if (this.goToNextWsPage) {
                    this.wsCurrentPage = this.lastWsPageNumber
                }
            }
        },

        methods: {
            messages() {
                router.push({path: `/request/messages/${this.id}`})
            },

            securityButtonVisible() {
                return this.$hasAccess("document")
            },

            onRequestRecive: function(data) {
                this.record = data.item;
            },

            onWsMessagesRecive: function(data) {
                this.goToNextWsPage = this.isWsOnLastPage && this.showWsLastPageSetting
                this.wsCollection = data.collection
                this.wsTotal = data.total
                this.wsIncomingTotal = data.incoming
                this.wsOutboundTotal = data.outbound
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

            format: function (code) {
                try {
                    return JSON.stringify(JSON.parse(code), null, 2)
                } catch (e) {
                    return code
                }
            },

            requestSubscribe: function() {
                return this.httpSubscription = this.subscribe(
                    "sibsribe.request",
                    msg => this.onRequestRecive(msg.data),
                    {"id": parseInt(this.id)}
                )
            },

            wsSubscribe: function() {
                return this.wsSubscription = this.subscribe(
                    "sibsribe.request.messages",
                    msg => this.onWsMessagesRecive(msg.data),
                    {
                        "id": parseInt(this.id),
                        "page.size": this.wsPerPage,
                        "page": this.wsCurrentPage
                    }
                )
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
            ps.$on('settings:change', configuration => {
                this.showWsLastPageSetting = configuration.showWsLastPage
            })
            ps.$emit('settings:fire')
        },
        
        destroyed: function() {
            this.wsUnsubscribe()
            this.httpUnsubscribe()
        }
    }
</script>

