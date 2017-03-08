<template>
    <div>
        <b-table striped hover :items="items" :fields="fields" :current-page="currentPage" :per-page="perPage" :filter="filter">
            <template slot="name" scope="item"> {{item.value}} </template>
            <template slot="position" scope="item"> {{item.value}} </template>
            <template slot="action" scope="item">
                <b-dropdown text="Действия" variant="success" split>
                    <a class="dropdown-item" href="#">Удалить</a>
                    <a class="dropdown-item" href="#">Переместить</a>
                    <a class="dropdown-item" href="#">Отправить</a>
                </b-dropdown>
            </template>
        </b-table>
        
        <div class="justify-content-center row my-1">
            <b-pagination size="md" :total-rows="this.items.length" :per-page="perPage" v-model="currentPage"/>
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
                {name: "Andrew", position: "Manager by people"}
            ],
            currentPage: 1,
            perPage: 5,
            filter: null
        })
    }
</script>


<style type="text/css">
    .sorting {
        cursor: pointer;
    }
</style>