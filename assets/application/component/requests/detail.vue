<template>
    <div class="row box box-direction-row">
        <div class="col-5 box box-direction-column">
            <b-card header="Request info" class="box box-direction-column"> 
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
        <div class="col-7 box box-direction-column">
            <b-card no-block show-footer no-body class="box box-direction-column">
                <b-tabs small pills card no-fade>
                    <b-tab title="Request headers">
                        <ul class="list-group" v-if="record">
                            <li class="list-group-item" v-for="value, key in record.reqheaders">
                                <span class="key-name">{{key}}:</span> <code>{{value}}</code> 
                            </li>
                        </ul>
                        <alert v-else message="Records not found"></alert>
                    </b-tab>
                    <b-tab title="Response headers">
                        <ul class="list-group" v-if="record">
                            <li class="list-group-item" v-for="(value, key) in record.resheaders">
                                <span class="key-name">{{key}}:</span> <code>{{value}}</code> 
                            </li>
                        </ul>
                        <alert v-else message="Records not found"></alert>
                    </b-tab>
                    <b-tab title="WebSocket messages" v-if="!isNotWs">
                        <ul class="list-group" v-if="record">
                            <li class="list-group-item aiodebugger__ws-list-group-item" v-for="(key, index) in wsCollection">
                                <i class="fa fa-arrow-up" aria-hidden="true" v-if="key.direction == 'OUTBOUND'"></i>
                                <i class="fa fa-arrow-down" aria-hidden="true" v-else></i>
                                <code>{{key.time}}</code>
                                
                                <i class="fa fa-eye pointer align-middle float-right" @click="showWsDetail(index)" aria-hidden="true"></i>
                                
                                <b-modal ref="wsDetail" title="Detail websocket message info"
                                         @shown="onDetailShown"
                                         @hidden="onDetailHidden"
                                         hide-footer>
                                    <pre><code>{{format(key.msg)}}</code></pre>
                                </b-modal>
                            </li>
                        </ul>
                        <alert v-else message="Records not found"></alert>
                    </b-tab>
                </b-tabs>
                <div slot="footer" v-if="!isNotWs">
                    <div class="container-fluid">
                        <div class="row" v-if="wsCollection && wsCollection.length > 0">
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
                                <div class="justify-content-center">
                                    <b-pagination :limit="5"
                                                  :total-rows="wsTotal"
                                                  :per-page="wsPerPage"
                                                  v-model="wsCurrentPage"
                                                  size="md"/>
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
    import {ps} from '@/utils';

    export default {
        mixins: [WebSocketService.mixin],
        data: function() {
            return {
                record: {},
                wsCurrentPage: 1,
                wsPerPage: 25,
                wsTotal: 0,
                wsCollection: [],
                goToNextWsPage: false,
                showWsLastPageSetting: false
            }
        },
        props: {
            id: String
        },
        computed: {
            isNotWs: function() {
                return !(this.wsCollection || {}).length;
            },

            isWsOnLastPage: function() {
                return this.wsCurrentPage == this.lastWsPageNumber;
            },

            lastWsPageNumber: function() {
                return Math.ceil(this.wsTotal / this.wsPerPage);
            }
        },
        watch: {
            wsCurrentPage: function(page) {
                this.wsUnsubscribe(() => this.wsSubscribe());
            },

            wsCollection: function() {
                if (this.goToNextWsPage) {
                    this.wsCurrentPage = this.lastWsPageNumber;
                }
            }
        },
        methods: {

            securityButtonVisible() {
                return this.$hasAccess("document");
            },

            onRequestRecive: function(data) {
                this.record = data.item;
            },

            onWsMessagesRecive: function(data) {
                this.goToNextWsPage = this.isWsOnLastPage && this.showWsLastPageSetting;
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

            format: function (code) {
                try {
                    return JSON.stringify(JSON.parse(code), null, 2);
                } catch (e) {
                    return code;
                }
            },

            requestSubscribe: function() {
                return this.httpSubscription = this.subscribe(
                    "sibsribe.request",
                    msg => this.onRequestRecive(msg.data),
                    {"id": parseInt(this.id)}
                );
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
                );
            },

            wsUnsubscribe: function(onComplete) {
                this.unsibscribe(this.wsSubscription, onComplete);
            },

            httpUnsubscribe: function(onComplete) {
                this.unsibscribe(this.httpSubscription, onComplete);
            }
        },

        created: function() {
            this.wsSubscribe();
            this.requestSubscribe();
            ps.$on('settings:change', configuration => {
                this.showWsLastPageSetting = configuration.showWsLastPage;
            });
            ps.$emit('settings:fire')
        },
        
        destroyed: function() {
            this.wsUnsubscribe();
            this.httpUnsubscribe();
        }
    }
</script>


<style lang="stylus" scoped>
    .aiodebugger__ws-list-group-item
        display block
    .key-name 
        margin-right: 5px
        
    .badge
        padding 12px
</style>
