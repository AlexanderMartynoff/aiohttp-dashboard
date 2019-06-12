<template>
    <div class="container-fluid my-3">
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

                    <template slot="status" slot-scope="record">
                        <span class="badge" :class="getStatusClassByCode(record.value)">
                            {{record.value}}
                        </span>
                    </template>

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
    import _ from "lodash"
    import {EventService} from '@/websocket'
    import {router} from '@/router'


    export default {
        data: () => ({
            fields: {
                status: {label: 'Status'},
                path: {label: 'Path'},
                method: {label: 'Method'},
                starttime: {label: 'Begin time'},
                stoptime: {label: 'End time'},
            },

            requests: [],
            page: 1,
        }),
        methods: {
            details: function(id) {
                router.push({path: `/request/detail/${id}`})
            },

            getStatusClassByCode(code) {
                if (_.startsWith(code, 4)) {
                    return 'badge-warning'
                } else if (_.startsWith(code, 5)) {
                    return 'badge-danger'
                } else {
                    return 'badge-success'
                }
            },

            loadRequests() {
                return this.$axios.get('/api/request').then(requests => {
                    this.requests = requests
                }) 
            }
        },

        created: function() {
            this.$event = EventService.create()

            this.$event.on('http', message => {
                this.loadRequests()
            });
            
            this.loadRequests()
        },
        
        destroyed: function() {
            this.$event.off()
        }
    }
</script>

