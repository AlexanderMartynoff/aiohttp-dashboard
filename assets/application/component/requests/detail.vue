<template>
    <div class="row">
        <div class="col-5">

            <b-card header="Request info">
                <ul class="list-group">
                    <li class="list-group-item">
                        Path:&nbsp;<code>{{record.path}}</code> 
                    </li>
                    <li class="list-group-item">
                        Begin time:&nbsp;<code>{{record.begintime}}</code> 
                    </li>
                    <li class="list-group-item">
                        Done time:&nbsp;<code>{{record.donetime}}</code> 
                    </li>
                </ul>
            </b-card>

        </div>
        <div class="col-7">
            <b-card no-block>
                <b-tabs small card no-fade>
                    <b-tab title="Request headers" active>
                        <ul class="list-group">
                            <li class="list-group-item" v-for="value, key in record.reqheaders">
                                {{key}}:&nbsp;<code>{{value}}</code> 
                            </li>
                        </ul>
                    </b-tab>
                    <b-tab title="Response headers" >
                        <ul class="list-group">
                            <li class="list-group-item" v-for="(value, key) in record.resheaders">
                                {{key}}:&nbsp;<code>{{value}}</code> 
                            </li>
                        </ul>
                    </b-tab>
                    <b-tab title="WebSocket messages" :disabled="!record.ws_request_msg" ref="tabWs">
                        <ul class="list-group">
                            <li class="list-group-item aiod__ws-list-group-item" v-for="(key, index) in record.ws_request_msg">
                                <i class="fa fa-arrow-circle-right" aria-hidden="true"></i>
                                <code>{{key.time}}</code>
                                <kbd><i>{{key.size}}</i></kbd> 
                                <div class="pull-right">
                                    <b-btn size="sm" class="pointer" @click="wsDetail(index)">
                                        <i class="fa fa-eye" aria-hidden="true"></i>
                                    </b-btn>
                                </div>
                                <b-modal ref="wsDetail"
                                         title="Detail websocket message info"
                                         hide-footer>
                                    <pre><code>{{format(key.msg)}}</code></pre>
                                </b-modal>
                            </li>
                        </ul>
                    </b-tab>
                </b-tabs>
            </b-card>

        </div>
    </div>
</template>


<script>
    import {WebSocketService} from '@/websocket';

    export default {
        data: () => ({record: {}}),
        props: {id: String},
        methods: {
            onDataRecive: function(data) {
                this.record = data || {};
            },
            wsDetail: function(index) {
                this.$refs.wsDetail[index].show();
            },
            format: function (code) {
                try {
                    return JSON.stringify(JSON.parse(code), null, 2); 
                } catch (e) {
                    return code;
                }
            }
        },
        created: function() {
            WebSocketService.instance.send({
                endpoint: "fetch.request",
                data: {"id": parseInt(this.id)}
            }, msg => this.onDataRecive(msg.data));
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
</style>