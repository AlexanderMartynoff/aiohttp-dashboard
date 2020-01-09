import {
    format,
    isSameYear,
    isSameDay,
    isSameMonth
} from 'date-fns'
import _ from 'lodash'

function formatDateTime(dateTime, inlcudeMs=false) {

    if (_.isNull(dateTime) || _.isUndefined(dateTime)) {
        return
    }

    let today = new Date()
    let pattern = `HH:mm:ss`

    if (!isSameDay(dateTime, today)) {
        pattern = `dd ${pattern}`
    }

    if (!isSameMonth(dateTime, today)) {
        pattern = `MM-${pattern}`
    }

    if (!isSameYear(dateTime, today)) {
        pattern = `yyyy-${pattern}`
    }

    if (inlcudeMs) {
        pattern += `:SSS`
    }

    return format(dateTime, pattern)
}

export {formatDateTime}