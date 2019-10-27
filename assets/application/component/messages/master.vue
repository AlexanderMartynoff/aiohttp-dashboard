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
                <b-card class="shadow h-100" title="Messages">
                    <b-table :responsive="true"
                             :hover="true"
                             :items="messages"
                             :fields="fields"
                             :show-empty="true"
                             empty-html="Records not found"
                             class="table-pointer"
                             striped>

                        <template v-slot:cell(direction)="direction">
                            <i class="fas" :class="getStatusClassByDirection(direction)"></i>
                        </template>

                    </b-table>

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
    import {formatDateTime} from '@/misc'
    import _ from "lodash"

    export default {
        data () {
            return {
                message: {},
                messages: [],
                fields: [
                    {
                        key: 'direction',
                        label: '',
                        tdClass: 'icon-td',
                        thClass: 'icon-th',
                    },
                    {
                        key: 'datetime',
                        label: 'Datetime',
                    },
                    {
                        key: 'size',
                        label: 'Size',
                        formatter: value => _.isString(value) ? value.length : 0
                    },
                ],
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
            getStatusClassByDirection(value) {
                return value === 'INCOMING' ? 'fa-arrow-circle-down' : 'fa-arrow-circle-up';
            },

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
                    this.messages = _.map(messages, message => _.merge(message, {
                        datetime: formatDateTime(message.time, true),
                    }))
                }) 
            },

            loadMessagesInfo() {
                return this.$axios.get(`/api/request/message/status`, {
                    params: {
                        request: this.id,
                    }
                }).then(info => {
                    if (info.websocket) {
                        this.incomingLength = info.websocket.countincoming
                        this.outcomingLength = info.websocket.countoutcoming
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
                conditions: {request: this.id},
            })

            this.loadMessages()
            this.loadMessagesInfo()
        },
        
        destroyed () {
            this.$event.off()
        }
    }
</script>


