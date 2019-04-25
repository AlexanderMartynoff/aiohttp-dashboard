<template>
    <div class="container-fluid">
        <div class="row mt-3 mb-3">
            <div class="col-md-12">
                <b-card class="shadow" title="Requests">
                    <b-table @row-clicked="(item, index) => details(item.id, index)" 
                             :responsive="true"
                             :hover="true"
                             :items="items"
                             :fields="fields"
                             striped
                             class="table-pointer">
                    </b-table>
                </b-card>
            </div>
        </div>
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
            items: [],
            currentPage: 1,
            perPage: 50,
            filter: null
        }),
        methods: {
            details: function(id) {
                router.push({path: `/request/detail/${id}`})
            }
        },
        created: function() {
            this.subscription = this.subscribe("sibsribe.requests", msg => {
                this.items = msg.data;
            });
        },
        destroyed: function() {
            this.unsibscribe(this.subscription);
        }
    }
</script>

