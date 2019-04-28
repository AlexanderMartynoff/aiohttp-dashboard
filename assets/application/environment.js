function getParameter(name) {
    const node = document.querySelector(`meta[name='${name}']`)

    if (node) {
        return node.content
    }

    throw new Error(`Parameter \`${name}\` not found in document head`)
}

export default {
    getParameter,
}
