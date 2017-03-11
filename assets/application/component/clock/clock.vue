<template>
    <span>{{time}}</span>    
</template>


<script>
export default {
    created: function() {
        setInterval(() => {
            this.time ++;
        }, 1000);
    },
    data: function() {
        return {
            time: 0
        }
    }
}
</script>
