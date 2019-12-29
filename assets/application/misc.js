import {format} from 'date-fns'
import _ from 'lodash'

function formatDateTime(dateTime, inlcudeMs=false) {

    if (_.isNull(dateTime) || _.isUndefined(dateTime)) {
        return
    }

    let pattern = `yyyy-MM-dd H:mm:ss`

    if (inlcudeMs) {
        pattern += `:SSS`
    }

    return format(dateTime, pattern)
}


export {formatDateTime}