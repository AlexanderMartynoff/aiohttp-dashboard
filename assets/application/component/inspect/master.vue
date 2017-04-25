<template>
  <b-card class="flex-card grey-card-bg" show-footer show-header>
        <b-table v-if="items.length"
                 @row-clicked="(item, index) => details(item.id, index)"
                 :items="items"
                 :fields="fields"
                 :current-page="currentPage"
                 :per-page="perPage"
                 striped>

        </b-table>

        <alert v-else message="Записей не найдено"></alert>

        <span slot="header">
            <i class="fa fa-globe" aria-hidden="true"></i> Inspection
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
        mixins: [WebSocketService.mixin],
        data: () => ({
            fields: {
                path: {label: 'Path'},
                method: {label: 'Method'},
                handler: {label: 'Handler'}
            },
            items: [],
            currentPage: 1,
            perPage: 50,
            filter: null
        }),
        methods: {
            details: function(id) {
                router.push({path: `/inspect/detail/${id}`})
            }
        },
        created: function() {
            this.send('fetch.routes', response => this.items = response.data);
        }
    }
</script>


<style lang="stylus" scoped>
.websocket_icon
    margin-right 5px
</style>