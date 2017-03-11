<template>
    <div>
        <b-modal ref="modal">
            <h3 slot="modal-header">Заголовок</h3>
            <b-dropdown slot="modal-footer" text="Действия" variant="success" size="sm" split>
                 <a class="dropdown-item" href="#">Удалить</a>
                 <a class="dropdown-item" href="#">Переместить</a>
                 <a class="dropdown-item" href="#">Отправить</a>
            </b-dropdown>
        </b-modal>

        <b-table striped hover :items="items" :fields="fields" :current-page="currentPage" :per-page="perPage" :filter="filter">
            <template slot="name" scope="item"> {{item.value}} </template>
            <template slot="position" scope="item"> {{item.value}} </template>
            <template slot="action" scope="item">
                <b-dropdown text="Действия" variant="success" @click="openModal" size="sm" split>
                    <a class="dropdown-item" href="#">Удалить</a>
                    <a class="dropdown-item" href="#">Переместить</a>
                    <a class="dropdown-item" href="#">Отправить</a>
                </b-dropdown>
            </template>
        </b-table>
        
        <div class="justify-content-center row my-1">
            <b-pagination size="sm" :total-rows="this.items.length" :per-page="perPage" v-model="currentPage"/>
        </div>
    </div>
</template>


<script type="text/javascript">
    export default {
        data: () => ({
            fields: {
                name: {label: 'Имя', sortable: true},
                position: {label: 'Должность'},
                action: {label: 'Действия'}
            },
            items: [
                {name: "Alex", position: "Driver"},
                {name: "Andrew", position: "Manager by people"},
                {name: "John", position: "Director"},
                {name: "Mikhail", position: "Ticher"},
                {name: "John", position: "Director"},
                {name: "Mikhail", position: "Ticher"},
                {name: "Alex", position: "Driver"},
                {name: "Andrew", position: "Manager by people"},
                {name: "Mikhail", position: "Ticher"},
                {name: "John", position: "Director"},
                {name: "Mikhail", position: "Ticher"},
                {name: "Alex", position: "Driver"},
                {name: "Andrew", position: "Manager by people"},
                {name: "Alex", position: "Driver"},
                {name: "Andrew", position: "Manager by people"}
            ],
            currentPage: 1,
            perPage: 5,
            filter: null
        }),
        methods: {
            openModal: function(arg){
                this.$refs.modal.show();
            }
        }
    }
</script>


<style type="text/css">
    .sorting {
        cursor: pointer;
    }
</style>