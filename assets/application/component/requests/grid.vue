<template>
  <b-card class="flex-card grey-card-bg" show-footer show-header>
        <b-table v-if="items.length"
                 @row-clicked="(item, index) => details(item.id, index)"
                 :items="items"
                 :fields="fields"
                 :current-page="currentPage"
                 :per-page="perPage"
                 class="table-pinter table-hover"
                 striped>

            <template slot="status" scope="item">
                {{item.item.status}}/{{item.item.reason}}
            </template>
        </b-table>

        <alert v-else message="Записей не найдено"></alert>

        <span slot="header">
            <i class="fa fa-globe" aria-hidden="true"></i> Requests
        </span>

        <small slot="footer">
            <div v-if="items.length" class="justify-content-center row">
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
                status: {label: 'Status'}
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
            this.subscription = WebSocketService.instance.subscribe("sibsribe.requests", msg => {
                this.items = msg.data;
            });
        },
        destroyed: function() {
            WebSocketService.instance.unsibscribe(this.subscription);
        }
    }
</script>


<style lang="stylus" scoped>
.websocket_icon
    margin-right 5px
</style>

<style lang="stylus">
.table-pinter tr
    cursor pointer
</style>