<template>

    <div class="container-fluid">
        <div class="row mt-3 mb-3">
            <div class="col-md-12">
                <b-card class="shadow" title="Routes">
                    <b-table v-if="items.length"
                             @row-clicked="(item, index) => details(item, index)"
                             :items="items"
                             :fields="fields"
                             :current-page="currentPage"
                             :per-page="perPage"
                             :hover="true"
                             :responsive="true"
                             class="table-pointer"
                             striped>

                        <template slot="path" scope="item">
                            {{item.item.info.path || item.item.info.prefix + ' -> ' + item.item.info.directory}}
                        </template>
                    </b-table>

                    <alert v-else message="Records not found"></alert>


                    <b-modal ref="sourceDetail" title="Source code" size="lg" class="modal-huge" centered hide-footer>
                        <pre><code>{{selected.source}}</code></pre>
                    </b-modal>

                </b-card>
            </div>
        </div>
    </div>

</template>


<script type="text/javascript">
    
    import {WebSocketService} from '@/websocket';
    import {router} from '@/router';

    export default {
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
        }
    }
</script>


<style lang="stylus" scoped>
.websocket_icon
    margin-right 5px
</style>
