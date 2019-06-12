<template>
    <div class="container-fluid my-3">

        <bar sticky="top">
            <b-nav>
                <b-nav-item active>
                    <i class="fas fa-arrows-alt-v"></i> {{bothLength}}
                    <i class="fa fa-long-arrow-alt-down"></i> {{incomingLength}}
                    <i class="fa fa-long-arrow-alt-up" aria-hidden="true"></i> {{outcomingLength}}
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
                    <pre><code>{{format(message.body)}}</code></pre>
                </b-modal>
            </div>
        </div>

        <bar v-if="messages" sticky="bottom" align="center" :card="false">            
            <b-pagination :limit="3" :per-page="50" v-model="page" align="center"/>
        </bar>
    </div>
</template>


<script>
    import {EventService} from '@/websocket'

    export default {
        data () {
            return {
                message: {},
                messages: [],
                limit: 25,
                incomingLength: 0,
                outcomingLength: 0,
                page: 1,
            }
        },
        props: {
            id: String
        },

        computed: {
            bothLength() {
                return this.incomingLength + this.outcomingLength
            }
        },

        methods: {

            showDetail (message) {
                this.message = message
                this.$refs.detail.show()
            },

            onDetailShown () {
                this.$event.stop()
            },

            onDetailHidden () {
                this.$event.start()
            },

            truncate(string, limit=50) {
                if (string && string.length > limit) {
                    return string.substr(0, limit) + ' ...'
                }

                return string
            },

            format (code) {
                try {
                    return JSON.stringify(JSON.parse(code), null, 2)
                } catch (e) {
                    return code
                }
            },

            loadMessages() {
                return this.$axios.get(`/api/message`, {
                    params: {
                        request: this.id,
                        start: 0, 
                        limit: 25, 
                    }
                }).then(messages => {
                    this.messages = messages
                }) 
            },

            loadMessagesInfo() {
                return this.$axios.get(`/api/request/${this.id}/message/info`).then(info => {
                    if (info.websocket) {
                        this.incomingLength = info.websocket.length.incoming
                        this.outcomingLength = info.websocket.length.outcoming
                    }
                }) 
            },
        },

        created () {
            this.$event = EventService.create()

            this.$event.on('websocket', message => {
                this.loadMessages()
                this.loadMessagesInfo()
            }, {
                request: this.id,
            })

            this.loadMessages()
            this.loadMessagesInfo()
        },
        
        destroyed () {
            this.$event.off()
        }
    }
</script>


