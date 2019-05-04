<template type="text/html">
    <div class="container-fluid my-3">
        <div class="row mt-3 mb-3">
            
            <div class="col-md-6 mt-3 mt-md-0">
                <b-card class="shadow h-100" title="Time">
                    <h3>
                        <code>14:41</code> <br/>
                        <small class="text-muted">applicaion start time</small>
                    </h3>
                    <h3>
                        <code>1 day 12 hours 53 seconds</code> <br/>
                        <small class="text-muted">application work duration</small>
                    </h3>
                </b-card>
            </div>

            <div class="col-md-6 mt-3 mt-md-0">
                <b-card class="shadow h-100" title="Exceptions">
                    <h3>
                        <code>558 068</code> <br/>
                        <small class="text-muted">total number</small>
                    </h3>
                </b-card>
            </div>

        </div>
        <div class="row mt-3 mb-3">
            <div class="col-md-6">
                <b-card class="shadow h-100" title="Requests">
                    <h3>
                        <code>{{requestsCount}}</code> <br/>
                        <small class="text-muted">total number</small>
                    </h3>
                    <h3>
                        <code>558</code> <br/>
                        <small class="text-muted">number per second</small>
                    </h3>
                </b-card>
            </div>
            <div class="col-md-6 mt-3 mt-md-0">
                <b-card class="shadow h-100" title="Messages">
                    <h3>
                        <code>558 068</code> <br/>
                        <small class="text-muted">total number</small>
                    </h3>
                    <h3>
                        <code>558</code> <br/>
                        <small class="text-muted">number per second</small>
                    </h3>
                </b-card>
            </div>
        </div>
    </div>
</template>


<script type="text/javascript">
    import {WebSocketService} from '@/websocket';

    export default {
        mixins: [WebSocketService.mixin],
        data: () => ({
            requestsCount: 0,
            messagesCount: 0,
        }),
        methods: {
            requestsSubscribe() {
                this.requestsSubscribtion = this.subscribe('request.requests.count', message => {
                    this.requestsCount = message.data
                })
            },
        },

        created() {
            this.requestsSubscribe()
        }
    }
</script>
