<template>
    <div class="container-fluid my-3">

        <bar sticky="top">
            <b-nav>
                <b-nav-item active>
                    <i class="fas fa-arrows-alt-v"></i> {{bothLength}}
                    <i class="fa fa-long-arrow-alt-down"></i> {{incomingLength}}
                    <i class="fa fa-long-arrow-alt-up" aria-hidden="true"></i> {{outboundLength}}
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
                outboundLength: 0,
            }
        },
        props: {
            id: String
        },

        computed: {
            bothLength() {
                return this.incomingLength + this.outboundLength
            }
        },

        methods: {

            showDetail (message) {
                this.message = message
                this.$refs.detail.show()
            },

            onDetailShown () {
                this.wsUnsubscribe()
            },

            onDetailHidden () {
                this.wsSubscribe()
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

        },

        created () {
            this.$event = EventService.create()

            this.$event.on('websocket', message => {
                console.log(message)
            }, {
                request: this.id,
            })
        },
        
        destroyed () {
            this.$event.off()
        }
    }
</script>


