<template>
  <b-card class="flex-card grey-card-bg" show-footer show-header>
        <b-table v-if="items.length"
                 @row-clicked="(item, index) => details(item, index)"
                 :items="items"
                 :fields="fields"
                 :current-page="currentPage"
                 :per-page="perPage"
                 class="table-pinter table-hover"
                 striped>

            <template slot="path" scope="item">
                {{item.item.info.path || item.item.info.prefix + ' -> ' + item.item.info.directory}}
            </template>
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

        <b-modal ref="sourceDetail" title="Source code" size="lg" class="modal-huge" hide-footer>
            <pre><code>{{selected.source}}</code></pre>
        </b-modal>
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
            selected: {},
            items: [],
            currentPage: 1,
            perPage: 50,
            filter: null
        }),
        methods: {
            details: function(item, index) {
                this.selected = item;
                this.$refs.sourceDetail.show();
            }
        },
        created: function() {
            this.send('fetch.routes',
                response => this.items = response.data);
        }
    }
</script>


<style lang="stylus" scoped>
.websocket_icon
    margin-right 5px
</style>