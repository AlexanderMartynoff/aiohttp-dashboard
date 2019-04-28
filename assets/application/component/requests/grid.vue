<template>
    <div class="container-fluid">
        <div class="row mt-3 mb-3">
            <div class="col-md-12">
                <b-card class="shadow" title="Requests">
                    <b-table @row-clicked="(item, index) => details(item.id, index)" 
                             :responsive="true"
                             :hover="true"
                             :items="requests"
                             :fields="fields"
                             striped
                             class="table-pointer">
                    </b-table>
                </b-card>
            </div>
        </div>

        <bar v-if="requests" sticky="bottom" align="center" :card="false">            
            <b-pagination :limit="3" :per-page="50" v-model="page" align="center"/>
        </bar>
    </div>
</template>


<script type="text/javascript">
    import {WebSocketService} from '@/websocket';
    import {router} from '@/router';


    export default {
        mixins: [WebSocketService.mixin],
        data: () => ({
            fields: {
                status: {label: 'Status'},
                path: {label: 'Path'},
                method: {label: 'Method'},
                begintime: {label: 'Begin time'},
                donetime: {label: 'End time'},
            },

            requests: [],
            page: 1,
        }),
        methods: {
            details: function(id) {
                router.push({path: `/request/detail/${id}`})
            }
        },
        created: function() {
            this.subscription = this.subscribe('requests', message => {
                this.requests = message.data;
            });
        },
        destroyed: function() {
            this.unsibscribe(this.subscription);
        }
    }
</script>

