import {format} from 'date-fns'

function formatDateTime(dateTime, inlcudeMs=false) {
    let pattern = `yyyy-MM-dd H:mm:ss`

    if (inlcudeMs) {
        pattern += ` SSS`
    }

    return format(dateTime, pattern)
}


export {formatDateTime}