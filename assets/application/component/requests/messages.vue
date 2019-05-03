<template>
    <div class="container-fluid my-3">

        <bar sticky="top">
            <b-nav>
                <b-nav-item active>
                    <i class="fas fa-arrows-alt-v"></i> {{total}}
                    <i class="fa fa-long-arrow-alt-down"></i> {{incomingTotal}}
                    <i class="fa fa-long-arrow-alt-up" aria-hidden="true"></i> {{outboundTotal}}
                </b-nav-item>
            </b-nav>
        </bar>

        <div class="row mt-3 mb-3">
            <div class="col-md-12">
                <b-card class="shadow h-100" title="WebSocket">
                    <b-list-group>
                        <b-list-group-item v-for="message in messages"
                                           @click="showDetail(message)"
                                           button>

                            <i class="fas fa-long-arrow-alt-up" v-if="message.direction == 'OUTBOUND'"></i>
                            <i class="fa fa-long-arrow-alt-down" v-else></i>
                            {{message.time}}
                        </b-list-group-item>
                    </b-list-group>
                </b-card>

                <b-modal ref="detail"
                         title="Message"
                         @click.native.stop
                         @shown="onDetailShown"
                         @hidden="onDetailHidden"
                         hide-footer
                         centered>
                    <pre><code>{{format(message.msg)}}</code></pre>
                </b-modal>
            </div>
        </div>

        <bar v-if="messages" sticky="bottom" align="center" :card="false">            
            <b-pagination :limit="3" :total-rows="total" :per-page="limit" v-model="page" align="center"/>
        </bar>
    </div>
</template>


<script>
    import {WebSocketService} from '@/websocket'

    export default {
        mixins: [WebSocketService.mixin],
        data: function() {
            return {
                fields: {
                    direction: {
                        label: 'Direction',
                        class: 'text-center'
                    },
                    time: {
                        label: 'Time'
                    },
                },
                message: {},
                page: 1,
                limit: 25,
                total: 0,
                messages: [],
                incomingTotal: 0,
                outboundTotal: 0,
            }
        },
        props: {
            id: String
        },

        watch: {
            page: function(page) { 
                this.wsUnsubscribe(() => this.wsSubscribe())    
            },
        },

        methods: {

            onWsMessagesRecive: function(data) {
                this.messages = data.collection
                this.total = data.total
                this.incomingTotal = data.incoming
                this.outboundTotal = data.outbound
            },

            showDetail: function(message) {
                this.message = message
                this.$refs.detail.show()
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

            wsSubscribe: function() {
                this.wsSubscription = this.subscribe('request.messages', message => {
                    this.onWsMessagesRecive(message.data)
                }, {
                    'id': parseInt(this.id),
                    'limit': this.limit,
                    'page': this.page,
                })
            },

            wsUnsubscribe: function(onComplete) {
                this.unsibscribe(this.wsSubscription, onComplete)
            },
        },

        created: function() {
            this.wsSubscribe()
        },
        
        destroyed: function() {
            this.wsUnsubscribe()
        }
    }
</script>


