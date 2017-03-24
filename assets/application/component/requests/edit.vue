<template>
    <form>

        <div class="row">
            <div class="col">
                <button type="button" class="close" aria-label="Close" @click.prevent="onClick">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
        </div>

        <div class="form-group">
            <label>Path</label>
            <div class="form-control">{{record.path}}</div>
        </div>

        <div class="form-group">
            <label>Begin time</label>
            <input type="text" class="form-control" :value="record.begintime"/>
        </div>

        <div class="form-group">
            <label>Done time</label>
            <input type="text" class="form-control" :value="record.donetime"/>
        </div>
    </form>
</template>


<script>
    export default {
        props: ['record'],
        methods: {
            onClick: function() {
                this.$emit("request:edit:close");
            }
        }
    }
</script>