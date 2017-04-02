<template>
  <b-card header="Requests" class="flex-card" show-footer>
        <b-table striped :items="items" :fields="fields" :current-page="currentPage" :per-page="perPage" :filter="filter">
            <template slot="open" scope="item">
                <div class="text-right">
                    <b-btn size="sm" @click="details(item.item.id)">
                        <i class="fa fa-eye" aria-hidden="true"></i>
                    </b-btn>
                </div>
            </template>

            <template slot="status" scope="item">
                {{item.item.status}}/{{item.item.reason}}
            </template>
        </b-table>

        <small slot="footer">
            <div class="justify-content-center row">
                <b-pagination size="md" :total-rows="this.items.length" :per-page="perPage" v-model="currentPage"/>
            </div>
        </small>
    </b-card>
</template>


<script type="text/javascript">
    
    import {WebSocketService} from '@/websocket';
    import {router} from '@/router';

    export default {
        data: () => ({
            fields: {
                path: {label: 'Path'},
                method: {label: 'Method'},
                begintime: {label: 'Begin time'},
                donetime: {label: 'Done time'},
                status: {label: 'Status'},
                open: {label: String()},
            },
            items: [],
            currentPage: 1,
            perPage: 15,
            filter: null
        }),
        methods: {
            details: function(id) {
                router.push({path: `/request/detail/${id}`})
            }
        },
        created: function() {
            this.subscription = WebSocketService.instance.subcribe("sibsribe.requests", msg => {
                this.items = msg.data;
            });
        },
        destroyed: function() {
            WebSocketService.instance.unsibscribe(this.subscription);
        }
    }
</script>


<style lang="stylus" scoped>
</style>