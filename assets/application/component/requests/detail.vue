<template>
    <div class="row d-flex">
        <div class="col-5 d-flex align-items-stretch">
            <b-card header="Request info" class="flex-card">
                <ul class="list-group">
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
            </b-card>
        </div>
        <div class="col-7 d-flex align-items-stretch">
            <b-card no-block class="flex-card" show-footer>
                <b-tabs small card no-fade>
                    <b-tab title="Request headers" active>
                        <ul class="list-group">
                            <li class="list-group-item" v-for="value, key in record.reqheaders">
                                <span class="key-name">{{key}}:</span> <code>{{value}}</code> 
                            </li>
                        </ul>
                    </b-tab>
                    <b-tab title="Response headers">
                        <ul class="list-group">
                            <li class="list-group-item" v-for="(value, key) in record.resheaders">
                                <span class="key-name">{{key}}:</span> <code>{{value}}</code> 
                            </li>
                        </ul>
                    </b-tab>
                    <b-tab title="WebSocket messages" :disabled="!record.ws_messages" ref="tabWs">
                        <ul class="list-group">
                            <li class="list-group-item aiod__ws-list-group-item" v-for="(key, index) in record.ws_messages">
                                <i class="fa fa-arrow-circle-right" aria-hidden="true" v-if="key.direction == 'outbound'"></i>
                                <i class="fa fa-arrow-circle-left" aria-hidden="true" v-else></i>
                                <code>{{key.time}}</code>
                                <kbd><i>{{key.size}}</i></kbd> 
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
                    </b-tab>
                </b-tabs>

                <div slot="footer">
                    <span v-if="wsAllMsgs.length > 0">
                        <span class="badge badge-success">
                            <i class="fa fa-arrow-circle-down" aria-hidden="true"></i>
                            {{wsIncomingMsgs.length}}
                        </span>
                        <span class="badge badge-success">
                            <i class="fa fa-arrow-circle-up" aria-hidden="true"></i>
                            {{wsOutboundMsgs.length}}
                        </span>
                    </span>
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
                record: {}
            }
        },
        props: {
            id: String
        },
        computed: {
            wsIncomingMsgs: function() {
                return (this.record.ws_messages || []).filter(msg => msg.direction == "incoming");
            },
            wsOutboundMsgs: function() {
                return (this.record.ws_messages || []).filter(msg => msg.direction == "outbound");
            },
            wsAllMsgs: function() {
                return (this.record.ws_messages || []);
            }
        },
        methods: {
            onDataRecive: function(data) {
                this.record = data || {};
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
            wsSubscribe: function() {
                return this.subscription = WebSocketService.instance.send({
                    endpoint: "fetch.request",
                    data: {"id": parseInt(this.id)}
                }, msg => this.onDataRecive(msg.data), true);
            },
            wsUnsubscribe: function() {
                WebSocketService.instance.unsibscribe(this.subscription);
            }
        },
        created: function() {
            this.wsSubscribe();
        },
        destroyed: function() {
            this.wsUnsubscribe();
        }
    }
</script>


<style lang="stylus" scoped>
    .aiod__ws-list-group-item
        display block
    pre
        background #f7f7f9
        border-radius 5px
        padding 5px
    pre code
        color #bd4147
    .key-name 
        margin-right: 5px 
</style>