<template>
    <div class="row">
        <div class="col">
            <b-table striped hover :items="items" :fields="fields" :current-page="currentPage" :per-page="perPage" :filter="filter">
                <template slot="open" scope="item">
                    <b-btn size="sm" @click="details(item)">
                        <i class="fa fa-eye" aria-hidden="true"></i>
                    </b-btn>
                </template>
            </b-table>
            
            <div class="justify-content-center row">
                <b-pagination size="sm" :total-rows="this.items.length" :per-page="perPage" v-model="currentPage"/>
            </div>
        </div>
        <div class="col" v-if="editmode == true">
            <edit></edit>
        </div>
    </div>
</template>


<script type="text/javascript">
    
    import {WebSocketService} from '@/websocket';
    import EditComponent from '@/component/index/edit';

    export default {
        components: {edit: EditComponent},
        data: () => ({
            editmode: false,
            fullModeFields: {
                scheme: {label: 'Scheme'},
                host: {label: 'Host'},
                method: {label: 'Method'},
                path: {label: 'Path'},
                begintime: {label: 'Begin time'},
                donetime: {label: 'Done time'},
                open: {label: String()},
            },
            editModeFields: {
                host: {label: 'Host'},
                path: {label: 'Path'}
            },
            fields: {},
            items: [],
            currentPage: 1,
            perPage: 5,
            filter: null
        }),
        methods: {
            openModal: function(arg){
                this.$refs.modal.show();
            },

            details: function(item) {
                this.startEdit();
            },

            startEdit: function() {
                this.editmode = true;
                this.fields = this.editModeFields;
            },

            stopEdit: function() {
                this.fields = this.fullModeFields;
            }
        },
        created: function () {
            WebSocketService.instance.send({endpoint: "fetch.requests"}, msg => {
                this.items = msg.data;
            });
            this.fields = this.fullModeFields;
        }
    }
</script>
