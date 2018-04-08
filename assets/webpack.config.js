let path = require('path')
let CopyWebpackPlugin = require('copy-webpack-plugin')

let resolve = (dir) => {
    return path.join(__dirname, dir)
}


module.exports = {
    entry: {
        application: resolve('./application/application.js')
    },
    output: {
        path: resolve("../aiohttp_debugger/static/bundle"),
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
                test: /\.styl$/i,
                use: ['style-loader', 'css-loader', 'stylus-loader']
            },
            {
                test: /\.vue$/,
                loader: 'vue-loader'
            },
            {
                test: /\.js$/,
                loader: 'babel-loader',
                include: [resolve('application')],
                query: {
                    presets: 'es2015',
                    plugins: ['transform-es2015-destructuring', 'transform-object-rest-spread']
                }
            },
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader']
            }
        ]
    },
    plugins: [
        new CopyWebpackPlugin([
            { from: resolve('node_modules/bootstrap/dist/css/bootstrap.css') },
            { from: resolve('node_modules/@fortawesome/fontawesome-free-webfonts/css'), to: "font-awesome/css", ignore: ["*.map"] },
            { from: resolve('node_modules/@fortawesome/fontawesome-free-webfonts/webfonts'), to: "font-awesome/webfonts" },
        ])
    ]
}
