<template>
    <div class="container-fluid my-3">

        <cardnavbar sticky="top">
            <b-nav-item active>
                <i class="fas fa-arrows-alt-v"></i> {{total}}
                <i class="fa fa-long-arrow-alt-down"></i> {{wsIncomingTotal}}
                <i class="fa fa-long-arrow-alt-up" aria-hidden="true"></i> {{wsOutboundTotal}}
            </b-nav-item>
        </cardnavbar>

        <div class="row mt-3 mb-3">
            <div class="col-md-12">
                <b-card class="shadow h-100" title="WebSocket">
                    <ul class="list-group">

                        <b-list-group>
                            <b-list-group-item button v-for="(key, index) in collection" @click="showWsDetail(key)">
                                <code>{{key.time}}</code>
                            </b-list-group-item>
                        </b-list-group>
                    </ul>

                </b-card>

                <b-modal ref="wsDetail"
                         title="Message"
                         @click.native.stop
                         @shown="onDetailShown"
                         @hidden="onDetailHidden"
                         centered
                         hide-footer>
                    <pre><code>{{format(record.msg)}}</code></pre>
                </b-modal>
            </div>
        </div>

        <cardnavbar v-if="collection" sticky="bottom" align="center" :card="false">            
            <b-pagination :limit="3"
                          :total-rows="total"
                          :per-page="limit"
                          :hide-ellipsis="true"
                          v-model="page"
                          align="center"
                          size="md"/>
        </cardnavbar>
    </div>
</template>


<script>
    import {WebSocketService} from '@/websocket'
    import {ps} from '@/utils'

    export default {
        mixins: [WebSocketService.mixin],
        data: function() {
            return {
                record: {},
                page: 1,
                limit: 25,
                total: 0,
                collection: [],
                wsIncomingTotal: 0,
                wsOutboundTotal: 0,
            }
        },
        props: {
            id: String
        },
        methods: {

            onWsMessagesRecive: function(data) {
                this.collection = data.collection
                this.total = data.total
                this.wsIncomingTotal = data.incoming
                this.wsOutboundTotal = data.outbound
            },

            showWsDetail: function(record) {
                this.record = record
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


