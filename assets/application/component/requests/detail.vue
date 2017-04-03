<template>
    <div class="row d-flex">
        <div class="col-5 d-flex align-items-stretch">
            <b-card header="Request info" class="flex-card">
                <ul class="list-group" v-if="record">
                    <li class="list-group-item list-group-item-warning block" v-if="record.status || record.reason">
                        <div><span>{{record.status}}</span></div>
                        <div><small class="text-muted">{{record.reason}}</small></div>
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

                <alert v-else message="Записей не найдено"></alert>
            </b-card>
        </div>
        <div class="col-7 d-flex align-items-stretch">
            <b-card no-block class="flex-card" show-footer>
                <b-tabs small card no-fade ref="tabs">
                    <b-tab title="Request headers" active>
                        <ul class="list-group" v-if="record">
                            <li class="list-group-item" v-for="value, key in record.reqheaders">
                                <span class="key-name">{{key}}:</span> <code>{{value}}</code> 
                            </li>
                        </ul>
                        <alert v-else message="Записей не найдено"></alert>
                    </b-tab>
                    <b-tab title="Response headers">
                        <ul class="list-group" v-if="record">
                            <li class="list-group-item" v-for="(value, key) in record.resheaders">
                                <span class="key-name">{{key}}:</span> <code>{{value}}</code> 
                            </li>
                        </ul>
                        <alert v-else message="Записей не найдено"></alert>
                    </b-tab>
                    <b-tab title="WebSocket messages" :disabled="isNotWs" id="ws">
                        <ul class="list-group" v-if="record">
                            <li class="list-group-item aiodebugger__ws-list-group-item" v-for="(key, index) in wsCollection">
                                <i class="fa fa-arrow-circle-up" aria-hidden="true" v-if="key.direction == 'outbound'"></i>
                                <i class="fa fa-arrow-circle-down" aria-hidden="true" v-else></i>
                                <code>{{key.time}}</code>
                                <div class="pull-right">
                                    <b-btn size="sm" class="pointer" @click="showWsDetail(index)">
                                        <i class="fa fa-eye" aria-hidden="true"></i>
                                    </b-btn>
                                </div>
                                <b-modal ref="wsDetail" title="Detail websocket message info"
                                         @shown="onDetailShown"
                                         @hidden="onDetailHidden"
                                         hide-footer>
                                    <pre><code>{{format(key.msg)}}</code></pre>
                                </b-modal>
                            </li>
                        </ul>
                        <alert v-else message="Записей не найдено"></alert>
                    </b-tab>
                </b-tabs>

                <div slot="footer">
                    <div class="container-fluid">
                        <div class="row" v-if="wsCollection.length > 0">
                            <div class="col-md-auto">
                                <span>
                                    <span class="badge badge-success">
                                        <i class="fa fa-arrow-circle-down" aria-hidden="true"></i>
                                        {{wsIncomingTotal}}
                                    </span>
                                    <span class="badge badge-success">
                                        <i class="fa fa-arrow-circle-up" aria-hidden="true"></i>
                                        {{wsOutboundTotal}}
                                    </span>
                                </span>
                            </div>
                            <div class="col-10">
                                <div class="justify-content-center row">
                                    <b-pagination size="md" :total-rows="wsTotal" :per-page="wsPerPage" v-model="wsCurrentPage"/>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </b-card>
        </div>
    </div>
</template>


<script>
    import {WebSocketService} from '@/websocket';

    export default {
        data: function() {
            return {
                record: {},
                wsCurrentPage: 1,
                wsPerPage: 10,
                wsTotal: 0,
                wsCollection: []
            }
        },
        props: {
            id: String
        },
        computed: {
            isNotWs: function() {
                return this.wsCollection == undefined;
            }
        },
        watch: {
            wsCurrentPage: function(page) {
                this.wsUnsubscribe(() => {
                    this.wsSubscribe();
                })
            }
        },
        methods: {
            onRequestRecive: function(data) {
                console.log(data);
                this.record = data.item;
            },
            onWsMessagesRecive: function(data) {
                this.wsCollection = data.collection;
                this.wsTotal = data.total;
                this.wsIncomingTotal = data.incoming;
                this.wsOutboundTotal = data.outbound;
            },
            showWsDetail: function(index) {
                this.$refs.wsDetail[index].show();
            },
            onDetailShown: function() {
                this.wsUnsubscribe();
            },
            onDetailHidden: function() {
                this.wsSubscribe();
            },
            onWsTabSelect: function() {},
            format: function (code) {
                try {
                    return JSON.stringify(JSON.parse(code), null, 2);
                } catch (e) {
                    return code;
                }
            },
            requestSubscribe: function() {
                return this.subscription = WebSocketService.instance.subscribe(
                    "sibsribe.request",
                    msg => this.onRequestRecive(msg.data),
                    {"id": parseInt(this.id)}
                );
            },
            wsSubscribe: function() {
                return this.subscription = WebSocketService.instance.subscribe(
                    "sibsribe.request.messages",
                    msg => this.onWsMessagesRecive(msg.data),
                    {
                        "id": parseInt(this.id),
                        "perpage": this.wsPerPage,
                        "page": this.wsCurrentPage
                    }
                );
            },
            wsUnsubscribe: function(onComplete) {
                WebSocketService.instance.unsibscribe(this.subscription, onComplete);
            }
        },
        created: function() {
            this.wsSubscribe();
            this.requestSubscribe();
        },
        mounted: function() {
            this.$refs.tabs.$el.querySelectorAll(".nav-item");
        },
        destroyed: function() {
            this.wsUnsubscribe();
        }
    }
</script>


<style lang="stylus" scoped>
    .aiodebugger__ws-list-group-item
        display block
    pre
        background #f7f7f9
        border-radius 5px
        padding 5px
    pre code
        color #bd4147
    .key-name 
        margin-right: 5px
        
    .badge
        padding 12px
</style>