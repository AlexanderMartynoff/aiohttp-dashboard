<template>
    <div class="container-fluid my-3">

        <cardnavbar sticky="top">
            <b-nav-item active>
                <i class="fas fa-arrows-alt-v"></i> {{wsTotal}}
                <i class="fa fa-long-arrow-alt-down"></i> {{wsIncomingTotal}}
                <i class="fa fa-long-arrow-alt-up" aria-hidden="true"></i> {{wsOutboundTotal}}
            </b-nav-item>
        </cardnavbar>

        <div class="row mt-3 mb-3">
            <div class="col-md-12">
                <b-card class="shadow h-100" title="WebSocket">
                    <ul class="list-group">

                        <b-list-group>
                            <b-list-group-item button v-for="(key, index) in wsCollection" @click="showWsDetail(key)">
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
                    <pre><code>{{format(wsRecord.msg)}}</code></pre>
                </b-modal>
            </div>
        </div>

        <cardnavbar v-if="wsCollection" sticky="bottom" align="center" :card="false">            
            <b-pagination :limit="3"
                          :total-rows="wsTotal"
                          :per-page="wsPerPage"
                          :hide-ellipsis="true"
                          v-model="wsCurrentPage"
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
        },

        created: function() {
            this.wsSubscribe()
        },
        
        destroyed: function() {
            this.wsUnsubscribe()
        }
    }
</script>


