var path = require('path')
var CopyWebpackPlugin = require('copy-webpack-plugin')

function resolve(dir) {
    return path.join(__dirname, dir)
}


module.exports = {
    entry: {
        application: './application/application.js'
    },
    output: {
        path: "../unixterm/static/bundle",
        filename: '[name].js',
        publicPath: '/static'
    },
    resolve: {
        extensions: ['.js', '.vue'],
        alias: {
            '@': resolve('application'),
            'vue$': 'vue/dist/vue.js'
        }
    },
    module: {
        rules: [
            {
                test: /\.vue$/,
                loader: 'vue-loader'
            },
            {
                test: /\.js$/,
                loader: 'babel-loader',
                include: [resolve('application')]
            }
        ]
    },
    plugins: [
        new CopyWebpackPlugin([
            {from: resolve('node_modules/bootstrap/dist/css/bootstrap.css')},
        ])
    ]
}