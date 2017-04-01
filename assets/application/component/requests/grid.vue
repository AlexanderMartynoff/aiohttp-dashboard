<template>
    <div class="row">
        <div class="col">
            <b-table striped :items="items" :fields="fields" :current-page="currentPage" :per-page="perPage" :filter="filter">
                <template slot="open" scope="item">
                    <div class="text-right">
                        <b-btn size="sm" @click="details(item.item.id)">
                            <i class="fa fa-eye" aria-hidden="true"></i>
                        </b-btn>
                    </div>
                </template>
            </b-table>
            
            <div class="justify-content-center row">
                <b-pagination size="sm" :total-rows="this.items.length" :per-page="perPage" v-model="currentPage"/>
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
                host: {label: 'Host'},
                path: {label: 'Path'},
                method: {label: 'Method'},
                begintime: {label: 'Begin time'},
                donetime: {label: 'Done time'},
                open: {label: String()},
            },
            items: [],
            currentPage: 1,
            perPage: 5,
            filter: null
        }),
        methods: {
            details: function(id) {
                router.push({path: `/request/detail/${id}`})
            }
        },
        created: function () {
            WebSocketService.instance.send({endpoint: "sibsribe.requests"}, msg => {
                this.items = msg.data;
            }, true);
        }
    }
</script>


<style lang="stylus" scoped>
    button
        cursor: pointer
</style>